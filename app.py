"""Web demo: upload a requirements document, watch the pipeline stages, read and download the report.

    streamlit run app.py

Uses the same validator.pipeline.run as the CLI, so the report is the same one the CLI writes.
"""
import tempfile
from pathlib import Path

import streamlit as st

from validator import config, pipeline, report
from validator.llm import Gemini
from validator.models import Report

SAMPLE = Path(__file__).parent / "docs" / "requirements.md"
SUBMITTED = Path(__file__).parent / "reports" / "report.json"
SEVERITY_RU = {"critical": "критичных", "major": "существенных", "minor": "незначительных"}

st.set_page_config(page_title="Проверка требований", page_icon="📋", layout="wide")
st.title("Агент проверки требований")
st.caption("ISO/IEC/IEEE 29148:2018 (п. 5.2.5, 5.2.6) и IEEE 830 (п. 4.3). Отчёт на русском.")

with st.sidebar:
    st.header("Настройки")
    model = st.text_input("Модель Gemini", value=config.MODEL)
    use_cache = st.checkbox("Брать ответы LLM из кэша", value=True,
                            help="Повторный прогон того же документа не тратит запросы бесплатного тарифа.")
    if not config.API_KEY:
        st.error("Нет GEMINI_API_KEY: скопируйте .env.example в .env и вставьте ключ.")

uploaded = st.file_uploader("Документ требований", type=["pdf", "docx", "md", "txt"])
use_sample = st.toggle(f"Взять пример из репозитория ({SAMPLE.relative_to(SAMPLE.parents[1])})",
                       value=uploaded is None)

source_name = uploaded.name if uploaded else (SAMPLE.name if use_sample else None)
start = st.button("Проверить", type="primary",
                  disabled=not source_name or (uploaded is not None and not config.API_KEY))

if start and not uploaded and SUBMITTED.exists():
    # the sample shows the submitted v1.0 report: instant, and visitors of a public demo
    # don't burn the free-tier quota (20 requests/day per model) on a document already checked
    st.session_state["report"] = Report.model_validate_json(SUBMITTED.read_text(encoding="utf-8"))
    st.session_state["source"] = SAMPLE.name
    st.info("Показан отчёт, который агент v1.0 сделал по документу кейса. "
            "Чтобы прогнать агента вживую, загрузите свой файл.")
elif start:
    with tempfile.TemporaryDirectory() as tmp:
        if uploaded:
            path = Path(tmp) / uploaded.name  # keep the original name: it goes into the report passport
            path.write_bytes(uploaded.getvalue())
        else:
            path = SAMPLE
        llm = Gemini(model, config.API_KEY, use_cache=use_cache, fallbacks=config.FALLBACK_MODELS)
        with st.status("Проверка документа…", expanded=True) as status:
            rep = pipeline.run(str(path), llm, on_stage=lambda s: status.write(f"→ {s}"))
            status.update(label="Готово", state="complete", expanded=False)
    st.session_state["report"] = rep
    st.session_state["source"] = source_name

rep = st.session_state.get("report")
if rep is not None:
    counts = {k: sum(1 for f in rep.findings if f.severity == k) for k in SEVERITY_RU}
    cols = st.columns(5)
    cols[0].metric("Требований", len(rep.requirements))
    cols[1].metric("Нарушений", len(rep.findings))
    for col, (sev, label) in zip(cols[2:], SEVERITY_RU.items()):
        col.metric(label.capitalize(), counts[sev])

    v = rep.verdict
    (st.success if v.ready_for_development else st.error)(
        f"Начинать разработку: {'да' if v.ready_for_development else 'нет'}; "
        f"тестирование: {'да' if v.ready_for_testing else 'нет'}. {v.summary}")

    md = report.render(rep)
    stem = Path(st.session_state.get("source") or "report").stem
    c1, c2 = st.columns(2)
    c1.download_button("Скачать отчёт (.md)", md, file_name=f"report-{stem}.md", mime="text/markdown")
    c2.download_button("Скачать данные (.json)", rep.model_dump_json(indent=2),
                       file_name=f"report-{stem}.json", mime="application/json")
    st.divider()
    st.markdown(md)
