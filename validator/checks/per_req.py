"""LLM-проверка каждого требования по criteria.REQUIREMENT.

ЗАГЛУШКА. Батчами по нескольку требований за вызов (лимиты бесплатного тарифа),
llm.ask(prompt, schema=<модель со списком FindingDraft>) → Finding(**d.model_dump(), scope="requirement").
"""
from typing import List

from ..llm import LLM
from ..models import Document, Finding, Requirement


def check(doc: Document, reqs: List[Requirement], llm: LLM) -> List[Finding]:
    return []
