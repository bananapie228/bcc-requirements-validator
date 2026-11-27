"""LLM review of the requirement set as a whole against criteria.SET.

Two focused passes instead of one broad prompt: a single prompt covering everything
spread the model thin and missed the contradictions that matter most.
"""
from typing import List

from .. import criteria, prompts
from ..llm import LLM
from ..models import Document, Finding, FindingList, Requirement
from . import accept
from .per_req import format_requirements

# pass name (= prompt template) -> criteria it may report
PASSES = {
    "set_consistency": ["set_consistent", "set_feasible", "set_comprehensible"],
    # scenario walk-through of requirements on the same behaviour: weaker models miss these
    # conflicts unless asked for them on their own
    "set_interactions": ["set_consistent", "set_feasible"],
    "set_completeness": ["set_complete", "set_validatable", "traceable", "ranked", "modifiable"],
}


def check(doc: Document, reqs: List[Requirement], llm: LLM) -> List[Finding]:
    findings = []
    for name, codes in PASSES.items():
        subset = {c: criteria.SET[c] for c in codes}
        prompt = prompts.render(name, criteria=criteria.as_prompt(subset),
                                requirements=format_requirements(reqs), document=doc.numbered())
        resp = llm.ask(prompt, FindingList, system=prompts.render("system"))
        findings += accept(resp.findings, "set", {r.rid for r in reqs}, subset)
    return findings
