from tests.fakes import FakeLLM
from validator import loaders, verdict
from validator.models import Finding, Verdict

DOC = loaders.load("docs/requirements.md")
OPTIMISTIC = Verdict(ready_for_development=True, ready_for_testing=True, summary="ok", top_fixes=[])


def _finding(severity):
    return Finding(id="F-001", scope="set", requirement_ids=[], criterion="set_consistent",
                   severity=severity, quote="q", problem="Противоречие X", recommendation="r", line=1)


def test_critical_finding_overrides_optimistic_llm():
    v = verdict.decide(DOC, [], [_finding("critical")], FakeLLM({Verdict: OPTIMISTIC}))
    assert not v.ready_for_development and not v.ready_for_testing


def test_llm_decides_when_no_critical_findings_and_sees_them():
    llm = FakeLLM({Verdict: OPTIMISTIC})
    v = verdict.decide(DOC, [], [_finding("minor")], llm)
    assert v.ready_for_development
    assert "F-001" in llm.prompts[0] and "Противоречие X" in llm.prompts[0]
