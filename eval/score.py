"""Score agent reports against the golden defect set.

    python eval/score.py reports/report.json
    python eval/score.py reports/report.json reports/baseline.json   # side-by-side comparison

Works offline: reads only the JSON reports (validator's report.json or eval/baseline.py output)
and eval/golden.yaml. A finding counts for a golden defect when its line is one of the defect's
lines and its text has one of the defect's keywords (see the header of golden.yaml).
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

GOLDEN = Path(__file__).with_name("golden.yaml")


@dataclass
class Defect:
    id: str
    title: str
    lines: List[int]
    keywords: List[str] = field(default_factory=list)
    key: bool = False


@dataclass
class Score:
    name: str
    findings: int
    hits: Dict[str, List[str]]  # defect id -> ids of the findings that matched it
    unmatched: List[str]  # findings that match no golden defect

    @property
    def found(self) -> int:
        return sum(1 for v in self.hits.values() if v)

    def recall(self) -> float:
        return self.found / len(self.hits) if self.hits else 0.0


def load_golden(path: Path = GOLDEN) -> List[Defect]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Defect(id=d["id"], title=d["title"], lines=[int(x) for x in d["lines"]],
                   keywords=[str(k) for k in d.get("keywords") or []], key=bool(d.get("key")))
            for d in data["defects"]]


def _has_keyword(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return True
    text = text.lower()
    # keyword must start a word: "дат" matches "дата", "по дате", not "кандидат"
    return any(re.search(r"(?<!\w)" + re.escape(k.lower()), text) for k in keywords)


def matches(finding: dict, defect: Defect) -> bool:
    line: Optional[int] = finding.get("line")
    if line is None or int(line) not in defect.lines:
        return False
    text = " ".join(str(finding.get(k) or "") for k in ("quote", "problem", "recommendation"))
    return _has_keyword(text, defect.keywords)


def score(report: dict, golden: List[Defect], name: str = "") -> Score:
    findings = report.get("findings", [])
    hits: Dict[str, List[str]] = {d.id: [] for d in golden}
    unmatched = []
    for i, f in enumerate(findings, 1):
        fid = f.get("id") or f"#{i}"
        matched = [d for d in golden if matches(f, d)]
        for d in matched:
            hits[d.id].append(fid)
        if not matched:
            unmatched.append(fid)
    return Score(name=name, findings=len(findings), hits=hits, unmatched=unmatched)


def render(scores: List[Score], golden: List[Defect]) -> str:
    keys = [d for d in golden if d.key]
    head = "| Дефект | Ключевой | " + " | ".join(s.name for s in scores) + " |"
    out = [head, "|" + " :--- |" * (2 + len(scores))]
    for d in golden:
        cells = [", ".join(s.hits[d.id]) if s.hits[d.id] else "✗" for s in scores]
        out.append(f"| {d.id}. {d.title} | {'да' if d.key else ''} | " + " | ".join(cells) + " |")
    out.append("")
    for s in scores:
        key_found = sum(1 for d in keys if s.hits[d.id])
        out.append(f"**{s.name}**: найдено {s.found}/{len(golden)} эталонных дефектов "
                   f"({s.recall():.0%}), ключевых {key_found}/{len(keys)}; "
                   f"находок всего {s.findings}, вне эталона {len(s.unmatched)}.")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Доля эталонных дефектов, найденных агентом.")
    ap.add_argument("reports", nargs="+", help="report.json агента и/или бейзлайна")
    ap.add_argument("--golden", default=str(GOLDEN))
    ap.add_argument("--min-recall", type=float, default=None,
                    help="код выхода 1, если у первого отчёта доля ниже порога (0..1)")
    a = ap.parse_args(argv)

    golden = load_golden(Path(a.golden))
    scores = [score(json.loads(Path(p).read_text(encoding="utf-8")), golden, name=Path(p).stem)
              for p in a.reports]
    print(render(scores, golden))
    if a.min_recall is not None and scores[0].recall() < a.min_recall:
        print(f"\nНиже порога {a.min_recall:.0%}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
