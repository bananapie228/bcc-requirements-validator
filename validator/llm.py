"""LLM seam. Modules receive an LLM object instead of building a client themselves,
so they can be tested offline (see tests/fakes.py)."""
import hashlib
import json
import time
from pathlib import Path
from typing import Protocol, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
    model: str

    def ask(self, prompt: str, schema: Type[T], system: str = "") -> T:
        """Return a response that matches the pydantic schema. Network/rate-limit errors are handled inside the adapter."""
        ...


class Gemini:
    """Google Gemini adapter: JSON schema, temperature=0, retries on 429/5xx, on-disk cache."""

    def __init__(self, model: str, api_key: str, cache_dir: Path = Path(".cache/llm"), use_cache: bool = True):
        if not api_key:
            raise SystemExit("Нет GEMINI_API_KEY: скопируйте .env.example в .env и вставьте ключ.")
        from google import genai  # lazy import: tests and keyless runs don't load the SDK

        self.model = model
        self._client = genai.Client(api_key=api_key)
        self._cache_dir = cache_dir
        self._use_cache = use_cache

    def ask(self, prompt: str, schema: Type[T], system: str = "") -> T:
        from google.genai import errors, types

        key_src = json.dumps([self.model, system, prompt, schema.model_json_schema()], ensure_ascii=False)
        cache_file = self._cache_dir / f"{hashlib.sha256(key_src.encode()).hexdigest()}.json"
        if self._use_cache and cache_file.exists():
            return schema.model_validate_json(cache_file.read_text(encoding="utf-8"))

        cfg = types.GenerateContentConfig(
            system_instruction=system or None,
            temperature=0,
            response_mime_type="application/json",
            response_schema=schema,
        )
        attempts = 5
        for attempt in range(attempts):
            try:
                resp = self._client.models.generate_content(model=self.model, contents=prompt, config=cfg)
                # text is None when the answer was blocked or cut off; truncated JSON fails validation
                result = schema.model_validate_json(resp.text or "")
                break
            except errors.APIError as e:
                # 429 = free-tier rate limit, 5xx = overload; other errors won't be fixed by retrying
                if e.code not in (429, 500, 503) or attempt == attempts - 1:
                    raise
                time.sleep(20 * (attempt + 1))
            except ValidationError:
                if attempt == attempts - 1:
                    raise SystemExit(f"Модель {self.model} {attempts} раз вернула пустой или неполный ответ "
                                     f"для {schema.__name__}. Попробуйте другую модель (--model).")

        self._cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(result.model_dump_json(), encoding="utf-8")
        return result
