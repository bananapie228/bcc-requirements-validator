from validator import grounding, loaders, report
from validator.models import Finding, Report, RunInfo, Verdict

DOC = loaders.load("docs/requirements.md")


def test_md_loads_with_title():
    assert DOC.title == "Уведомление о расходах по карте"
    assert any("Ф-3" in line for line in DOC.lines)


def test_locate_ignores_markdown_and_spacing():
    line = grounding.locate(DOC, "Ф-1. Держатель  активной карты KZT")
    assert line is not None and "Ф-1" in DOC.lines[line - 1]


def test_locate_spans_lines_and_rejects_invented_quotes():
    assert grounding.locate(DOC, "Сервис передаёт push на отправку в течение минуты") is not None
    assert grounding.locate(DOC, "Система должна работать быстро") is None


def _finding(quote):
    return Finding(scope="requirement", requirement_ids=["R-01"], criterion="verifiable",
                   severity="critical", quote=quote, problem="p", recommendation="r")


def test_ground_drops_hallucinated_findings():
    kept = grounding.ground(DOC, [_finding("REST type"), _finding("нет такого текста")])
    assert [f.quote for f in kept] == ["REST type"]


def test_report_renders_all_sections():
    f = _finding("REST type")
    f.id, f.line = "F-001", 1
    rep = Report(run=RunInfo(document="d", date="t", model="m", agent_version="v"),
                 requirements=[], findings=[f],
                 verdict=Verdict(ready_for_development=False, ready_for_testing=False, summary="s", top_fixes=[]))
    md = report.render(rep)
    for n in range(1, 7):
        assert f"## {n}." in md
    assert "F-001" in md


def test_ground_drops_unknown_criterion():
    f = _finding("REST type")
    f.criterion = "made_up"
    assert grounding.ground(DOC, [f]) == []


def test_pipeline_end_to_end_with_fake_llm():
    from tests.fakes import FakeLLM
    from validator import pipeline, segmenter
    from validator.models import FindingDraft, FindingList

    seg = segmenter.SegmentResponse(requirements=[segmenter.SegmentItem(
        doc_id="Ф-3", section="Функциональные требования",
        text="На карту приходится максимум один такой push за календарный месяц.")])
    real = FindingDraft(requirement_ids=["R-01"], criterion="set_consistent", severity="critical",
                        quote="максимум один такой push за календарный месяц", problem="p", recommendation="r")
    invented = real.model_copy(update={"quote": "push отправляется дважды"})
    llm = FakeLLM({
        segmenter.SegmentResponse: seg,
        FindingList: FindingList(findings=[real, invented]),
        Verdict: Verdict(ready_for_development=True, ready_for_testing=True, summary="s", top_fixes=[]),
    })

    rep = pipeline.run("docs/requirements.md", llm)

    assert rep.run.model == "fake"
    assert [r.doc_id for r in rep.requirements] == ["Ф-3"]
    # both passes get [real, invented]: per_req rejects the set-level criterion,
    # grounding drops the invented quote, so one set finding survives
    assert [(f.id, f.scope) for f in rep.findings] == [("F-001", "set")]
    assert {f.quote for f in rep.findings} == {real.quote}
    assert not rep.verdict.ready_for_development
    assert "F-001" in report.render(rep)


def test_locate_prefers_match_at_or_after_hint_line():
    first = grounding.locate(DOC, "Да / Нет")
    later = grounding.locate(DOC, "Да / Нет", near=first + 5)
    assert later >= first + 5


def test_dedup_drops_requirement_finding_already_reported_by_set_pass():
    a = _finding("REST type")
    a.line = 1
    b = a.model_copy(update={"scope": "set", "criterion": "set_consistent", "requirement_ids": ["R-01", "R-02"]})
    dup = a.model_copy()
    assert grounding.dedup([a, b, dup]) == [b]


def test_dedup_collapses_set_findings_on_same_place_across_criteria():
    a = _finding("REST type").model_copy(update={"scope": "set", "criterion": "set_consistent", "line": 1})
    b = a.model_copy(update={"criterion": "traceable"})
    assert grounding.dedup([a, b]) == [a]
