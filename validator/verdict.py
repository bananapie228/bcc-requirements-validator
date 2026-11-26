"""Final verdict: can development and testing start.

STUB: "no critical findings -> ready". TODO: LLM verdict grounded in the findings
(top_fixes must reference specific F-xxx IDs).
"""
from typing import List

from .llm import LLM
from .models import Document, Finding, Requirement, Verdict


def decide(doc: Document, reqs: List[Requirement], findings: List[Finding], llm: LLM) -> Verdict:
    critical = [f for f in findings if f.severity == "critical"]
    return Verdict(
        ready_for_development=not critical,
        ready_for_testing=not critical,
        summary=f"Критичных дефектов: {len(critical)}.",
        top_fixes=[f"{f.id}: {f.problem}" for f in critical[:5]],
    )
