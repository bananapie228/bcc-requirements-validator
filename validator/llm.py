"""LLM seam. Modules receive an LLM object instead of building a client themselves,
so they can be tested offline (see tests/fakes.py)."""
import hashlib
import json
import logging
import sys
import time
import warnings
from pathlib import Path
from typing import List, Optional, Protocol, Sequence, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)
# Per request. Sent to the server as its deadline too (X-Server-Timeout): segmenting a whole
# document on a thinking model took over 180 s, so keep this generous.
TIMEOUT_S = 600
# Overload (503) comes in waves of several minutes: wait it out (30+60+90+120 s) before falling back.
ATTEMPTS_PER_MODEL = 5
BACKOFF_S = 30


class LLM(Protocol):
    model: str

    def ask(self, prompt: str, schema: Type[T], system: str = "") -> T:
        """Return a response that matches the pydantic schema. Network/rate-limit errors are handled inside the adapter."""
        ...


class Gemini:
    """Google Gemini adapter: JSON schema, temperature=0, on-disk cache, retries, and fallback
    to the next model when one is overloaded, out of quota or keeps returning broken answers."""

    def __init__(self, model: str, api_key: str, cache_dir: Path = Path(".cache/llm"), use_cache: bool = True,
                 fallbacks: Sequence[str] = ()):
        if not api_key:
            raise SystemExit("Нет GEMINI_API_KEY: скопируйте .env.example в .env и вставьте ключ.")
        with warnings.catch_warnings():
            # import-time noise on older Pythons (end-of-life, LibreSSL) the user can't act on mid-run
            warnings.simplefilter("ignore")
            from google import genai  # lazy import: tests and keyless runs don't load the SDK
            from google.genai import types
        # thinking models attach a thought signature to every answer; the SDK warns about it each time
        logging.getLogger("google_genai.types").setLevel(logging.ERROR)

        self._models = [model] + [m for m in fallbacks if m != model]
        self._used: List[str] = []
        # without a timeout a stalled request hangs the whole run forever
        self._client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=TIMEOUT_S * 1000))
        self._cache_dir = cache_dir
        self._use_cache = use_cache

    @property
    def model(self) -> str:
        """Models that actually answered, in order — goes into the report passport."""
        return " → ".join(self._used) or self._models[0]

    def _cache_file(self, model: str, prompt: str, schema: Type[BaseModel], system: str) -> Path:
        key_src = json.dumps([model, system, prompt, schema.model_json_schema()], ensure_ascii=False)
        return self._cache_dir / f"{hashlib.sha256(key_src.encode()).hexdigest()}.json"

    def _answered(self, model: str) -> None:
        if model not in self._used:
            self._used.append(model)

    def ask(self, prompt: str, schema: Type[T], system: str = "") -> T:
        # Per model in order: its cache, then a live call. A fallback's cached answer must not
        # shadow a fresh answer from a better model that is available again.
        for model in list(self._models):
            cache_file = self._cache_file(model, prompt, schema, system)
            if self._use_cache and cache_file.exists():
                self._answered(model)
                return schema.model_validate_json(cache_file.read_text(encoding="utf-8"))
            result = self._ask_model(model, prompt, schema, system)
            if result is not None:
                self._answered(model)
                self._cache_dir.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(result.model_dump_json(), encoding="utf-8")
                return result
            # don't waste the next calls' retries on a model that just failed: try it last
            self._models.remove(model)
            self._models.append(model)
            print(f"[llm] {model} недоступна, переключаюсь на следующую модель", file=sys.stderr, flush=True)
        raise SystemExit(f"Ни одна модель не ответила ({', '.join(self._models)}). "
                         f"Попробуйте позже или задайте другие модели в .env.")

    def _ask_model(self, model: str, prompt: str, schema: Type[T], system: str) -> Optional[T]:
        """The parsed answer, or None when this model should be given up on."""
        import httpx
        from google.genai import errors, types

        cfg = types.GenerateContentConfig(
            system_instruction=system or None,
            temperature=0,
            response_mime_type="application/json",
            response_schema=schema,
        )
        for attempt in range(ATTEMPTS_PER_MODEL):
            print(f"[llm] {model}: {schema.__name__}, попытка {attempt + 1}", file=sys.stderr, flush=True)
            started = time.monotonic()
            try:
                resp = self._client.models.generate_content(model=model, contents=prompt, config=cfg)
                # text is None when the answer was blocked or cut off; truncated JSON fails validation
                result = schema.model_validate_json(resp.text or "")
                print(f"[llm] готово за {time.monotonic() - started:.0f} с", file=sys.stderr, flush=True)
                return result
            except errors.APIError as e:
                print(f"[llm] ошибка API {e.code}: {str(e)[:120]}", file=sys.stderr, flush=True)
                if e.code in (400, 404):
                    # this model rejects the request or is retired for this key: retrying won't help, the next may
                    return None
                # 429 = quota, 5xx = overload or server deadline; 401/403 = bad key, stop right away
                if e.code not in (429, 500, 503, 504):
                    raise
            except httpx.TimeoutException:
                print(f"[llm] нет ответа за {TIMEOUT_S} с", file=sys.stderr, flush=True)
            except ValidationError as e:
                print(f"[llm] ответ не по схеме ({e.error_count()} ошибок), длина {len(resp.text or '')}",
                      file=sys.stderr, flush=True)
            if attempt < ATTEMPTS_PER_MODEL - 1:
                time.sleep(BACKOFF_S * (attempt + 1))
        return None
