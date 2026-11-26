import sys
from typing import Collection, Iterable, List, Set

from ..models import Finding, FindingDraft


def accept(drafts: Iterable[FindingDraft], scope: str, known_rids: Set[str],
           criteria: Collection[str]) -> List[Finding]:
    """Turn LLM drafts into findings, keeping only requirement IDs the pass reviewed
    and criteria of the pass's own family (otherwise the report tables would show ✓ next to a defect).

    A requirement-level finding left with no valid ID is dropped: it cannot be attached anywhere.
    """
    out = []
    for d in drafts:
        rids = [r for r in d.requirement_ids if r in known_rids]
        if d.criterion not in criteria:
            print(f"[checks] отброшено, критерий {d.criterion!r} не из этого прохода", file=sys.stderr)
            continue
        if scope == "requirement" and not rids:
            print(f"[checks] отброшено, неизвестные требования {d.requirement_ids}", file=sys.stderr)
            continue
        out.append(Finding(**d.model_dump(exclude={"requirement_ids"}), requirement_ids=rids, scope=scope))
    return out
