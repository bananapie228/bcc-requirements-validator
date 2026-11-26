"""LLM review of the requirement set as a whole against criteria.SET."""
from typing import List

from .. import criteria, prompts
from ..llm import LLM
from ..models import Document, Finding, FindingList, Requirement
from . import accept
from .per_req import format_requirements


def check(doc: Document, reqs: List[Requirement], llm: LLM) -> List[Finding]:
    prompt = prompts.render("set_level", criteria=criteria.as_prompt(criteria.SET),
                            requirements=format_requirements(reqs), document=doc.numbered())
    resp = llm.ask(prompt, FindingList, system=prompts.render("system"))
    return accept(resp.findings, "set", {r.rid for r in reqs}, criteria.SET)
