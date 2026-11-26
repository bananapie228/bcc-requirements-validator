"""Final verdict: can development and testing start from this document."""
from typing import List

from . import prompts
from .llm import LLM
from .models import Document, Finding, Requirement, Verdict


def _format(findings: List[Finding]) -> str:
    return "\n".join(
        f"{f.id} [{f.severity}] {f.criterion} ({', '.join(f.requirement_ids) or 'set'}; line {f.line}): {f.problem}"
        for f in findings
    ) or "(no findings)"


def decide(doc: Document, reqs: List[Requirement], findings: List[Finding], llm: LLM) -> Verdict:
    n_critical = sum(f.severity == "critical" for f in findings)
    prompt = prompts.render("verdict", title=doc.title, n_requirements=str(len(reqs)),
                            n_critical=str(n_critical), findings=_format(findings))
    v = llm.ask(prompt, Verdict, system=prompts.render("system"))
    if n_critical:
        # hard rule, not left to the model: critical defects block the start of work
        v.ready_for_development = v.ready_for_testing = False
    return v
