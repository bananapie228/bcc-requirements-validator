"""Data contract shared by all modules."""
from typing import List, Literal, Optional

from pydantic import BaseModel

Severity = Literal["critical", "major", "minor"]


class Document(BaseModel):
    path: str
    title: str
    lines: List[str]  # document line N == lines[N - 1]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def numbered(self) -> str:
        """Text with line numbers — the form in which the document is sent to the LLM."""
        return "\n".join(f"{i}: {line}" for i, line in enumerate(self.lines, 1))


class Requirement(BaseModel):
    rid: str  # report-level ID: R-01, R-02, ...
    doc_id: Optional[str] = None  # ID as written in the document (e.g. Ф-1), None if unnumbered
    section: str  # document section the requirement comes from
    text: str  # verbatim quote from the document
    line: Optional[int] = None  # first line of the quote, set by grounding


class FindingDraft(BaseModel):
    """Exactly what the LLM fills in. Use as the response schema for llm.ask."""
    requirement_ids: List[str]  # Requirement.rid values; set-level findings may list several or none
    criterion: str  # code from criteria.py; unknown codes are dropped by grounding
    severity: Severity
    quote: str  # verbatim quote from the document; findings without one are rejected
    problem: str
    recommendation: str


class Finding(FindingDraft):
    """Pipeline finding: the LLM draft plus fields set by code, never by the LLM."""
    scope: Literal["requirement", "set"]
    source: Literal["llm", "rule"] = "llm"
    line: Optional[int] = None  # set by grounding
    id: str = ""  # F-001..., assigned by pipeline


class Verdict(BaseModel):
    ready_for_development: bool
    ready_for_testing: bool
    summary: str
    top_fixes: List[str]  # what to fix first, in priority order


class RunInfo(BaseModel):
    document: str
    date: str
    model: str
    agent_version: str


class Report(BaseModel):
    run: RunInfo
    requirements: List[Requirement]
    findings: List[Finding]
    verdict: Verdict
