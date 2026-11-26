"""Anchor quotes to document lines and drop findings whose quote is not in the document."""
import re
import sys
from bisect import bisect_right
from typing import List, Optional, Sequence

from .criteria import ALL
from .models import Document, Finding, Requirement


def _norm(s: str) -> str:
    s = s.lower().replace("ё", "е")
    s = re.sub(r"[«»\"“”„]", '"', s)
    s = re.sub(r"[–—]", "-", s)
    s = re.sub(r"[*`|#>]", " ", s)  # markdown and table markup
    return re.sub(r"\s+", " ", s).strip()


def locate(doc: Document, quote: str, near: Optional[int] = None) -> Optional[int]:
    """1-based line where the quote starts; None if the quote is not in the document.

    With `near`, the first occurrence at or after that line wins: short quotes repeat across the document.
    """
    q = _norm(quote)
    if not q:
        return None
    starts, parts, pos = [], [], 0
    for line in doc.lines:
        n = _norm(line)
        starts.append(pos)
        parts.append(n)
        pos += len(n) + 1
    text = " ".join(parts)
    first = text.find(q)
    if first < 0:
        return None
    if near:
        after = text.find(q, starts[min(near, len(starts)) - 1])
        if after >= 0:
            return bisect_right(starts, after)
    return bisect_right(starts, first)


def ground(doc: Document, findings: List[Finding], reqs: Sequence[Requirement] = ()) -> List[Finding]:
    """Keep only findings with a known criterion and a real quote; set their line."""
    req_line = {r.rid: r.line for r in reqs if r.line}
    kept = []
    for f in findings:
        near = min((req_line[r] for r in f.requirement_ids if r in req_line), default=None)
        f.line = locate(doc, f.quote, near)
        if f.criterion not in ALL:
            print(f"[grounding] отброшено, неизвестный критерий {f.criterion!r}", file=sys.stderr)
        elif f.line is None:
            print(f"[grounding] отброшено, цитаты нет в документе: {f.quote[:80]!r}", file=sys.stderr)
        else:
            kept.append(f)
    return kept


def dedup(findings: List[Finding]) -> List[Finding]:
    """Drop repeats: identical findings, and requirement findings a set finding already covers
    (same quote at the same line about a shared requirement — typically one contradiction seen by both passes)."""
    set_cover = [(f.line, _norm(f.quote), set(f.requirement_ids)) for f in findings if f.scope == "set"]
    seen, out = set(), []
    for f in findings:
        key = (f.scope, f.criterion, f.line, _norm(f.quote), tuple(sorted(f.requirement_ids)))
        covered = f.scope == "requirement" and any(
            line == f.line and quote == _norm(f.quote) and rids & set(f.requirement_ids)
            for line, quote, rids in set_cover)
        if key in seen or covered:
            continue
        seen.add(key)
        out.append(f)
    return out
