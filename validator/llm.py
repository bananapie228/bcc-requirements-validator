"""Шов к LLM. Модули получают объект LLM, а не создают клиента сами — так их можно тестировать
без сети (см. tests/fakes.py)."""
import hashlib
import json
import time
from pathlib import Path
from typing import Protocol, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
    model: str

    def ask(self, prompt: str, schema: Type[T], system: str = "") -> T:
        """Ответ строго по pydantic-схеме. Ошибки сети/лимитов — внутри адаптера."""
        ...


class Gemini:
    """Адаптер Google Gemini: JSON-схема, temperature=0, повторы при 429/5xx, кэш на диске."""

    def __init__(self, model: str, api_key: str, cache_dir: Path = Path(".cache/llm"), use_cache: bool = True):
        if not api_key:
            raise SystemExit("Нет GEMINI_API_KEY: скопируйте .env.example в .env и вставьте ключ.")
        from google import genai  # импорт тут: тесты и Streamlit без ключа не тянут SDK

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
        for attempt in range(5):
            try:
                resp = self._client.models.generate_content(model=self.model, contents=prompt, config=cfg)
                break
            except errors.APIError as e:
                # 429 — лимит бесплатного тарифа, 5xx — перегрузка; остальное повтором не лечится
                if e.code not in (429, 500, 503) or attempt == 4:
                    raise
                time.sleep(20 * (attempt + 1))

        result = schema.model_validate_json(resp.text)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(result.model_dump_json(), encoding="utf-8")
        return result
