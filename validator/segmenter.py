"""Split a document into individual requirements.

STUB: picks only explicitly numbered lines (Ф-1, NFR-2, ...).
TODO: LLM-based segmentation of every requirement statement (NFRs, data, integration,
acceptance criteria, API rules and parameters) with our own R-NN IDs, the document's
own ID in doc_id and a verbatim quote in text.
"""
import re
from typing import List

from .llm import LLM
from .models import Document, Requirement

_ID_LINE = re.compile(r"^[\s*\-]*([А-ЯA-Z]{1,5}-\d+)[.)]?\**\s*(.+)$")


def segment(doc: Document, llm: LLM) -> List[Requirement]:
    reqs, section = [], ""
    for line in doc.lines:
        if line.startswith("#"):
            section = line.strip("# ").strip()
        m = _ID_LINE.match(line)
        if m:
            reqs.append(Requirement(rid=f"R-{len(reqs) + 1:02d}", doc_id=m.group(1),
                                    section=section, text=m.group(2).strip()))
    return reqs
