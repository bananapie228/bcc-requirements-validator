"""Web demo: upload a requirements document, watch the pipeline stages, read and download the report.

    streamlit run app.py

Uses the same validator.pipeline.run as the CLI, so the report is the same one the CLI writes.
"""
import tempfile
from pathlib import Path

import streamlit as st

from validator import config, pipeline, report
from validator.llm import Gemini

SAMPLE = Path(__file__).parent / "docs" / "requirements.md"
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
start = st.button("Проверить", type="primary", disabled=not (source_name and config.API_KEY))

if start:
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
