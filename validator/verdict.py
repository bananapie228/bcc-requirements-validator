"""Итоговое заключение.

ЗАГЛУШКА: правило «нет критичных — можно начинать». Заменить на LLM-заключение
с опорой на находки (top_fixes — конкретные пункты со ссылками на F-xxx).
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
