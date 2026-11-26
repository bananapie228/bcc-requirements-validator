"""Контракт между модулями. Меняем только по договорённости всей команды."""
from typing import List, Literal, Optional

from pydantic import BaseModel

Severity = Literal["critical", "major", "minor"]


class Document(BaseModel):
    path: str
    title: str
    lines: List[str]  # строка N документа = lines[N - 1]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    def numbered(self) -> str:
        """Текст с номерами строк — так документ отдаём в LLM."""
        return "\n".join(f"{i}: {line}" for i, line in enumerate(self.lines, 1))


class Requirement(BaseModel):
    rid: str  # ID в отчёте: R-01, R-02, ...
    doc_id: Optional[str] = None  # ID в документе (Ф-1) или None, если номера не было
    section: str  # раздел документа: «Функциональные требования», «Часть B / Query-параметры»
    text: str  # дословная цитата из документа
    line: Optional[int] = None  # первая строка цитаты, заполняет grounding


class FindingDraft(BaseModel):
    """Ровно то, что заполняет LLM. Используйте как схему ответа в llm.ask."""
    requirement_ids: List[str]  # rid из Requirement; для проверки набора может быть несколько или пусто
    criterion: str  # код из criteria.py; неизвестный код отсекает grounding
    severity: Severity
    quote: str  # дословная цитата из документа — без неё находка не принимается
    problem: str
    recommendation: str


class Finding(FindingDraft):
    """Находка в конвейере: черновик + поля, которые заполняем мы, а не LLM."""
    scope: Literal["requirement", "set"]
    source: Literal["llm", "rule"] = "llm"
    line: Optional[int] = None  # заполняет grounding
    id: str = ""  # F-001..., присваивает pipeline


class Verdict(BaseModel):
    ready_for_development: bool
    ready_for_testing: bool
    summary: str
    top_fixes: List[str]  # что исправить в первую очередь, по порядку


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
