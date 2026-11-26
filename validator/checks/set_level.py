"""LLM-проверка набора по criteria.SET.

ЗАГЛУШКА. Противоречия между требованиями, критериями приёмки и API (часть B),
пропуски, трассируемость A↔B, единообразие терминов.
Схема ответа — список FindingDraft → Finding(**d.model_dump(), scope="set").
"""
from typing import List

from ..llm import LLM
from ..models import Document, Finding, Requirement


def check(doc: Document, reqs: List[Requirement], llm: LLM) -> List[Finding]:
    return []
