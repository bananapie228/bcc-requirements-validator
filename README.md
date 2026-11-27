# Агент проверки требований

ИИ-агент для статической проверки документа требований по ISO/IEC/IEEE 29148:2018 (п. 5.2.5, 5.2.6)
и IEEE Std 830-1998 (п. 4.3). Агент выделяет требования, проверяет каждое и весь набор и пишет отчёт на русском.

Кейс BCC-HUB × MNU FinTech Hackathon: https://github.com/BCC-HUB/ai-requirements-validator-task

- **Веб-демо:** https://bcc-requirements-validator.streamlit.app/ — пример показывает готовый отчёт v1.0,
  свой файл агент проверяет вживую (бесплатный ключ Gemini, 20 запросов в сутки на модель).
- **Отчёт по документу кейса:** [reports/report.md](reports/report.md), сделан агентом версии `v1.0`.
- **Презентация:** [docs/presentation.pdf](docs/presentation.pdf).

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

Если основная модель перегружена или недоступна ключу, агент сам переключается на запасные из
`GEMINI_FALLBACK_MODELS`. В паспорт отчёта записывается модель, которая на самом деле ответила.

**Лимиты бесплатного тарифа.** Google даёт 20 запросов в сутки на каждую модель в проекте. Один прогон делает
около 11 запросов, так что со свежим ключом прогон укладывается в лимит. Если лимит исчерпан (ошибка 429),
агент сразу переходит к запасной модели. Повторный прогон с теми же входными данными берёт ответы из кэша
`.cache/llm` и квоту не тратит.

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

Архитектурные решения:
- [ADR-0001](docs/adr/0001-pipeline-architecture.md) — устройство конвейера и что показали прогоны;
- [ADR-0002](docs/adr/0002-models-and-free-tier.md) — выбор модели и работа в лимитах бесплатного тарифа.

## Веб-демо

```bash
streamlit run app.py
```

Откроется страница в браузере: загрузите PDF / DOCX / MD / TXT (или возьмите `docs/requirements.md`),
нажмите «Проверить». Видны этапы конвейера, число нарушений по серьёзности и итог; отчёт можно скачать
в `.md` и `.json`. Демо вызывает тот же `validator.pipeline.run`, что и CLI, ключ берётся из того же `.env`.

## Оценка качества

`eval/golden.yaml` — 27 эталонных дефектов `docs/requirements.md` из ручного разбора, 5 из них ключевые
противоречия. `eval/score.py` считает, какую долю нашёл агент (находка засчитывается по номеру строки
и слову-маркеру).

```bash
python eval/score.py reports/report.json
```

Сравнение с бейзлайном «весь документ одним промптом» на той же модели:

```bash
python eval/baseline.py docs/requirements.md reports/baseline.json
python eval/score.py reports/report.json reports/baseline.json
```

Тестовые входы — в `samples/`: тот же документ в PDF и DOCX и второй документ другой предметной области
(`samples/password-reset.md`), чтобы проверить, что агент не подогнан под один файл:

```bash
python -m validator samples/requirements.pdf reports/report-pdf.md
python -m validator samples/password-reset.md reports/report-password-reset.md
```
