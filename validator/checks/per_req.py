"""LLM review of each requirement on its own against criteria.REQUIREMENT."""
from typing import List

from .. import criteria, prompts
from ..llm import LLM
from ..models import Document, Finding, FindingList, Requirement
from . import accept

# Requirements per LLM call: fewer calls for free-tier rate limits, small enough to stay thorough.
BATCH_SIZE = 8


def format_requirements(reqs: List[Requirement]) -> str:
    return "\n".join(
        f"{r.rid}" + (f" [{r.doc_id}]" if r.doc_id else "")
        + f" ({r.section}" + (f", line {r.line}" if r.line else "") + f"): {r.text}"
        for r in reqs
    )


def check(doc: Document, reqs: List[Requirement], llm: LLM) -> List[Finding]:
    findings = []
    for start in range(0, len(reqs), BATCH_SIZE):
        batch = reqs[start:start + BATCH_SIZE]
        prompt = prompts.render("per_req", criteria=criteria.as_prompt(criteria.REQUIREMENT),
                                batch=format_requirements(batch), document=doc.numbered())
        resp = llm.ask(prompt, FindingList, system=prompts.render("system"))
        findings += accept(resp.findings, "requirement", {r.rid for r in batch}, criteria.REQUIREMENT)
    return findings
