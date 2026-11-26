"""Привязка цитат к строкам документа и отсев находок без реальной цитаты."""
import re
import sys
from bisect import bisect_right
from typing import List, Optional

from .criteria import ALL
from .models import Document, Finding


def _norm(s: str) -> str:
    s = s.lower().replace("ё", "е")
    s = re.sub(r"[«»\"“”„]", '"', s)
    s = re.sub(r"[–—]", "-", s)
    s = re.sub(r"[*`|#>]", " ", s)  # разметка markdown и таблиц
    return re.sub(r"\s+", " ", s).strip()


def locate(doc: Document, quote: str) -> Optional[int]:
    """Номер строки (с 1), с которой начинается цитата; None — цитаты в документе нет."""
    q = _norm(quote)
    if not q:
        return None
    starts, parts, pos = [], [], 0
    for line in doc.lines:
        n = _norm(line)
        starts.append(pos)
        parts.append(n)
        pos += len(n) + 1
    idx = " ".join(parts).find(q)
    return None if idx < 0 else bisect_right(starts, idx)


def ground(doc: Document, findings: List[Finding]) -> List[Finding]:
    """Оставляет только находки с известным критерием и реальной цитатой; проставляет line."""
    kept = []
    for f in findings:
        f.line = locate(doc, f.quote)
        if f.criterion not in ALL:
            print(f"[grounding] отброшено, неизвестный критерий {f.criterion!r}", file=sys.stderr)
        elif f.line is None:
            print(f"[grounding] отброшено, цитаты нет в документе: {f.quote[:80]!r}", file=sys.stderr)
        else:
            kept.append(f)
    return kept
