# Агент проверки требований

ИИ-агент для статической проверки документа требований по ISO/IEC/IEEE 29148:2018 (п. 5.2.5, 5.2.6)
и IEEE Std 830-1998 (п. 4.3). Агент выделяет требования, проверяет каждое и весь набор и пишет отчёт на русском.

Кейс BCC-HUB × MNU FinTech Hackathon: https://github.com/BCC-HUB/ai-requirements-validator-task

## Быстрый старт

Нужен Python 3.9+ (рекомендуем 3.11+).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # вставьте GEMINI_API_KEY
python -m validator docs/requirements.md reports/report.md
```

**Ключ LLM.** Откройте https://aistudio.google.com/ → Get API key → создайте ключ (хватит бесплатного тарифа).
Вставьте его в `.env` в строку `GEMINI_API_KEY=`. Модель задаётся там же (`GEMINI_MODEL`) или флагом `--model`.

**Результат.** Отчёт в Markdown ляжет в указанный путь (`reports/report.md`), рядом — `report.json` с теми же данными.

**Форматы входа:** PDF, DOCX, MD, TXT.

Флаги: `--model <ID>` — другая модель Gemini; `--no-cache` — не брать ответы LLM из кэша `.cache/llm`
(по умолчанию повторный прогон с тем же входом не тратит запросы).

## Как работает

```
документ → чтение (строки с номерами) → нарезка на требования (LLM)
        → формальные проверки (без LLM) → проверка каждого требования (LLM) → проверка набора (LLM)
        → проверка цитат: находка без дословной цитаты из документа отбрасывается
        → итоговое заключение (LLM) → отчёт
```

| Модуль | Что делает |
| :--- | :--- |
| `validator/models.py` | контракт данных: Requirement, Finding, Verdict, Report |
| `validator/criteria.py` | критерии 29148 / IEEE 830 |
| `validator/loaders.py` | чтение PDF / DOCX / MD / TXT |
| `validator/llm.py` | шов LLM: адаптер Gemini (JSON-схема, повторы при лимитах, кэш); в тестах — `FakeLLM` |
| `validator/segmenter.py` | нарезка на требования |
| `validator/checks/` | `rules` (без LLM), `per_req`, `set_level` |
| `validator/grounding.py` | привязка цитат к строкам, отсев выдуманных |
| `validator/verdict.py` | итог: можно ли начинать разработку |
| `validator/report.py` | отчёт по шаблону `templates/report.md.j2` |

## Тесты

```bash
pytest -q
```

Архитектурные решения: [docs/adr/0001-pipeline-architecture.md](docs/adr/0001-pipeline-architecture.md).
