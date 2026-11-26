"""Prompt templates live next to this file as <name>.md and are filled with str.format."""
from pathlib import Path

_DIR = Path(__file__).parent


def render(name: str, **values: str) -> str:
    return (_DIR / f"{name}.md").read_text(encoding="utf-8").format(**values)
