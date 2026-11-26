"""LLM check of the whole requirement set against criteria.SET.

STUB. TODO: contradictions between requirements, acceptance criteria and the API spec,
gaps, traceability between linked documents, consistent terminology.
Response schema: list of FindingDraft -> Finding(**d.model_dump(), scope="set").
"""
from typing import List

from ..llm import LLM
from ..models import Document, Finding, Requirement


def check(doc: Document, reqs: List[Requirement], llm: LLM) -> List[Finding]:
    return []
