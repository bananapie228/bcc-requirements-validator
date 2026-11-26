"""Отчёт в Markdown из Report."""
from collections import Counter
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from . import criteria
from .models import Report

_env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"),
                   trim_blocks=True, lstrip_blocks=True)
_env.filters["cell"] = lambda s: str(s or "—").replace("|", "\\|").replace("\n", " ")

SEVERITY_RU = {"critical": "критичный", "major": "существенный", "minor": "незначительный"}


def render(report: Report) -> str:
    by_req = {r.rid: [f for f in report.findings if r.rid in f.requirement_ids and f.scope == "requirement"]
              for r in report.requirements}
    set_findings = [f for f in report.findings if f.scope == "set"]
    return _env.get_template("report.md.j2").render(
        r=report,
        by_req=by_req,
        set_findings=set_findings,
        counts=Counter(f.severity for f in report.findings),
        critical=[f for f in report.findings if f.severity == "critical"],
        REQ=criteria.REQUIREMENT,
        SET=criteria.SET,
        ALL=criteria.ALL,
        SEV=SEVERITY_RU,
    )
