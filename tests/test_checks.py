from tests.fakes import FakeLLM
from validator import loaders
from validator.checks import per_req, set_level
from validator.models import FindingDraft, FindingList, Requirement

DOC = loaders.load("docs/requirements.md")


def _reqs(n):
    return [Requirement(rid=f"R-{i:02d}", section="S", text=f"t{i}") for i in range(1, n + 1)]


def _draft(rids, criterion="verifiable"):
    return FindingDraft(requirement_ids=rids, criterion=criterion, severity="major",
                        quote="REST type", problem="p", recommendation="r")


def test_per_req_batches_requirements_and_marks_scope():
    llm = FakeLLM({FindingList: FindingList(findings=[_draft(["R-01"])])})
    findings = per_req.check(DOC, _reqs(per_req.BATCH_SIZE + 1), llm)

    assert len(llm.prompts) == 2
    assert "R-01" in llm.prompts[0] and "R-01" not in llm.prompts[1]
    assert {f.scope for f in findings} == {"requirement"}


def test_per_req_drops_findings_about_requirements_outside_the_batch():
    llm = FakeLLM({FindingList: FindingList(findings=[_draft(["R-99"]), _draft(["R-01", "R-77"])])})
    findings = per_req.check(DOC, _reqs(1), llm)
    assert [f.requirement_ids for f in findings] == [["R-01"]]


def test_set_level_is_one_call_and_keeps_document_level_findings():
    llm = FakeLLM({FindingList: FindingList(findings=[_draft([], "set_complete"), _draft(["R-02", "R-99"], "set_consistent")])})
    findings = set_level.check(DOC, _reqs(3), llm)

    assert len(llm.prompts) == 1
    assert [f.requirement_ids for f in findings] == [[], ["R-02"]]
    assert {f.scope for f in findings} == {"set"}


def test_passes_drop_criteria_from_the_other_family():
    llm = FakeLLM({FindingList: FindingList(findings=[_draft(["R-01"], "set_consistent"), _draft(["R-01"], "complete")])})
    assert [f.criterion for f in per_req.check(DOC, _reqs(1), llm)] == ["complete"]
    assert [f.criterion for f in set_level.check(DOC, _reqs(1), llm)] == ["set_consistent"]
