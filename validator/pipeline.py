"""Run orchestration. Single entry point shared by the CLI and the web demo."""
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Callable

from . import grounding, loaders, segmenter, verdict
from .checks import per_req, rules, set_level
from .llm import LLM
from .models import Report, RunInfo

_SEV_ORDER = {"critical": 0, "major": 1, "minor": 2}


def agent_version() -> str:
    try:
        return subprocess.run(["git", "describe", "--always", "--dirty", "--tags"],
                              cwd=Path(__file__).parent, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run(path: str, llm: LLM, on_stage: Callable[[str], None] = lambda s: None) -> Report:
    on_stage("Чтение документа")
    doc = loaders.load(path)

    on_stage("Нарезка требований")
    reqs = segmenter.segment(doc, llm)

    on_stage("Формальные проверки")
    findings = rules.check(doc, reqs)
    on_stage("Проверка каждого требования")
    findings += per_req.check(doc, reqs, llm)
    on_stage("Проверка набора требований")
    findings += set_level.check(doc, reqs, llm)

    on_stage("Проверка цитат")
    findings = grounding.ground(doc, findings, reqs)
    # sort before dedup: of two duplicates the first is kept, and it must be the more severe one
    findings.sort(key=lambda f: (_SEV_ORDER[f.severity], f.line or 0))
    findings = grounding.dedup(findings)
    for i, f in enumerate(findings, 1):
        f.id = f"F-{i:03d}"

    on_stage("Итоговое заключение")
    v = verdict.decide(doc, reqs, findings, llm)

    return Report(
        run=RunInfo(document=f"{doc.title} ({Path(path).name})",
                    date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    model=llm.model, agent_version=agent_version()),
        requirements=reqs, findings=findings, verdict=v,
    )
