"""LLM check of each requirement against criteria.REQUIREMENT.

STUB. TODO: batch several requirements per call (free-tier rate limits),
llm.ask(prompt, schema=<model with a list of FindingDraft>) → Finding(**d.model_dump(), scope="requirement").
"""
from typing import List

from ..llm import LLM
from ..models import Document, Finding, Requirement


def check(doc: Document, reqs: List[Requirement], llm: LLM) -> List[Finding]:
    return []
