"""Baseline "like everyone else": the whole document in one prompt, no segmentation,
no per-requirement passes, no rules. Used to show what the pipeline adds.

    python eval/baseline.py docs/requirements.md reports/baseline.json
    python eval/score.py reports/report.json reports/baseline.json

Same model and the same LLM seam as the agent, so the comparison is about the method.
Findings get a line number by plain quote search, so they can be scored by eval/score.py.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run as a script from the repo root

from validator import config, loaders  # noqa: E402
from validator.models import Document, FindingDraft  # noqa: E402

PROMPT = """Ты — аналитик требований. Найди дефекты в документе требований по ISO/IEC/IEEE 29148
(п. 5.2.5, 5.2.6) и IEEE 830 (п. 4.3). Для каждого дефекта дай дословную цитату из документа,
критерий, серьёзность (critical/major/minor), суть проблемы и рекомендацию. Пиши по-русски.

Документ (номер строки: текст):
{document}
"""


class BaselineAnswer(BaseModel):
    findings: List[FindingDraft]


def _norm(s: str) -> str:
    return re.sub(r"[\s*`|«»\"]+", " ", s).strip().lower()


def locate(doc: Document, quote: str) -> Optional[int]:
    """1-based line of the first line containing the quote (or the quote containing the line)."""
    q = _norm(quote)
    if not q:
        return None
    for i, line in enumerate(doc.lines, 1):
        n = _norm(line)
        if n and (q in n or (len(n) > 15 and n in q)):
            return i
    return None


def run(path: str, llm) -> dict:
    doc = loaders.load(path)
    ans = llm.ask(PROMPT.format(document=doc.numbered()), BaselineAnswer)
    findings = []
    for i, f in enumerate(ans.findings, 1):
        d = f.model_dump()
        d.update(id=f"B-{i:03d}", line=locate(doc, f.quote))
        findings.append(d)
    return {
        "run": {"document": f"{doc.title} ({Path(path).name})", "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "model": llm.model, "agent_version": "baseline"},
        "findings": findings,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Бейзлайн: весь документ одним промптом.")
    ap.add_argument("input")
    ap.add_argument("output", nargs="?", default="reports/baseline.json")
    ap.add_argument("--model", default=config.MODEL)
    ap.add_argument("--no-cache", action="store_true")
    a = ap.parse_args(argv)

    from validator.llm import Gemini

    llm = Gemini(a.model, config.API_KEY, use_cache=not a.no_cache, fallbacks=config.FALLBACK_MODELS)
    result = run(a.input, llm)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    grounded = sum(1 for f in result["findings"] if f["line"])
    print(f"Бейзлайн: {out} (находок {len(result['findings'])}, с найденной цитатой {grounded})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
