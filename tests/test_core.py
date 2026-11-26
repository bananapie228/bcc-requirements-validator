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


def test_pipeline_runs_without_network():
    from tests.fakes import FakeLLM
    from validator import pipeline

    rep = pipeline.run("docs/requirements.md", FakeLLM())
    assert rep.run.model == "fake"
    assert [f.id for f in rep.findings] == [f"F-{i:03d}" for i in range(1, len(rep.findings) + 1)]
    assert report.render(rep)
