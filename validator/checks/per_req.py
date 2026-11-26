"""LLM review of each requirement on its own against criteria.REQUIREMENT."""
from typing import List

from .. import criteria, prompts
from ..llm import LLM
from ..models import Document, Finding, FindingList, Requirement
from . import accept

# Requirements per LLM call. Each call resends the whole document and a thinking model takes minutes
# per call, so fewer, larger batches cut run time; 25 still leaves the model room to be thorough.
BATCH_SIZE = 25


def format_requirements(reqs: List[Requirement]) -> str:
    """One block per requirement; the header is metadata, only the `text:` line is document text."""
    return "\n\n".join(
        f"### {r.rid}\n"
        f"document ID: {r.doc_id or 'none'} | section: {r.section} | line: {r.line or 'unknown'}\n"
        f"text: {r.text}"
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
