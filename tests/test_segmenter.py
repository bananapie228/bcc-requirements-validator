from tests.fakes import FakeLLM
from validator import loaders, segmenter

DOC = loaders.load("docs/requirements.md")


def _llm(*items):
    out = segmenter.SegmentResponse(requirements=[segmenter.SegmentItem(**i) for i in items])
    return FakeLLM({segmenter.SegmentResponse: out})


def test_assigns_report_ids_keeps_doc_ids_and_locates_lines():
    llm = _llm(
        {"doc_id": "Ф-1", "section": "Функциональные требования",
         "text": "Держатель активной карты KZT задаёт целый порог от 1 000 до 1 000 000 ₸ включительно."},
        {"doc_id": None, "section": "Нефункциональные требования",
         "text": "Сервис передаёт push на отправку в течение минуты после получения события."},
    )
    reqs = segmenter.segment(DOC, llm)

    assert [r.rid for r in reqs] == ["R-01", "R-02"]
    assert [r.doc_id for r in reqs] == ["Ф-1", None]
    assert "Ф-1" in DOC.lines[reqs[0].line - 1]
    assert "в течение минуты" in DOC.lines[reqs[1].line - 1]


def test_sends_numbered_document_to_llm():
    llm = _llm()
    segmenter.segment(DOC, llm)
    assert "37: * **Ф-1.**" in llm.prompts[0]


def test_keeps_requirement_with_unlocatable_quote_but_without_line():
    reqs = segmenter.segment(DOC, _llm({"doc_id": None, "section": "X", "text": "пересказ, которого нет в тексте"}))
    assert len(reqs) == 1 and reqs[0].line is None
