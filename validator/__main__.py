"""python -m validator <document> <report.md> [--model ID] [--no-cache]"""
import argparse
import sys
from pathlib import Path

from . import config, pipeline, report
from .llm import Gemini


def main() -> None:
    ap = argparse.ArgumentParser(prog="python -m validator", description="Проверка документа требований")
    ap.add_argument("input", help="документ требований: .pdf, .docx, .md, .txt")
    ap.add_argument("output", help="куда записать отчёт (.md); рядом ляжет .json")
    ap.add_argument("--model", default=config.MODEL, help=f"ID модели Gemini (по умолчанию {config.MODEL})")
    ap.add_argument("--no-cache", action="store_true", help="не брать ответы LLM из кэша")
    a = ap.parse_args()
    llm = Gemini(a.model, config.API_KEY, use_cache=not a.no_cache)

    rep = pipeline.run(a.input, llm, on_stage=lambda s: print(f"→ {s}", file=sys.stderr))
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.render(rep), encoding="utf-8")
    out.with_suffix(".json").write_text(rep.model_dump_json(indent=2), encoding="utf-8")
    print(f"Отчёт: {out}  (требований {len(rep.requirements)}, нарушений {len(rep.findings)})", file=sys.stderr)


if __name__ == "__main__":
    main()
