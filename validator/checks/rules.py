"""Deterministic checks without the LLM (source="rule").

STUB. TODO: empty sections and table fields, "—" instead of a value, unticked
"Да / Нет" checklists, vague words, mixed units, missing version/date/approvers.
"""
from typing import List

from ..models import Document, Finding, Requirement


def check(doc: Document, reqs: List[Requirement]) -> List[Finding]:
    return []
