"""Split a document into individual requirements with the LLM."""
import sys
from typing import List, Optional

from pydantic import BaseModel

from . import grounding, prompts
from .llm import LLM
from .models import Document, Requirement


class SegmentItem(BaseModel):
    doc_id: Optional[str]
    section: str
    text: str


class SegmentResponse(BaseModel):
    requirements: List[SegmentItem]


def segment(doc: Document, llm: LLM) -> List[Requirement]:
    resp = llm.ask(prompts.render("segment", document=doc.numbered()), SegmentResponse,
                   system=prompts.render("system"))
    reqs = []
    for i, item in enumerate(resp.requirements, 1):
        line = grounding.locate(doc, item.text)
        if line is None:
            # kept: losing a requirement is worse than a missing line number in the table
            print(f"[segmenter] цитата требования не найдена в документе: {item.text[:80]!r}", file=sys.stderr)
        reqs.append(Requirement(rid=f"R-{i:02d}", doc_id=item.doc_id, section=item.section,
                                text=item.text, line=line))
    return reqs
