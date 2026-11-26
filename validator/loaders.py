"""Read an input document (PDF/DOCX/MD/TXT) into lines."""
from pathlib import Path

from .models import Document


def _read_pdf(path: Path) -> str:
    import fitz  # pymupdf

    with fitz.open(path) as pdf:
        return "\n".join(page.get_text() for page in pdf)


def _read_docx(path: Path) -> str:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    d = docx.Document(str(path))
    out = []
    for el in d.element.body.iterchildren():  # paragraphs and tables in document order
        if el.tag.endswith("}p"):
            out.append(Paragraph(el, d).text)
        elif el.tag.endswith("}tbl"):
            for row in Table(el, d).rows:
                out.append("| " + " | ".join(c.text.strip() for c in row.cells) + " |")
    return "\n".join(out)


def load(path: str) -> Document:
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".pdf":
        text = _read_pdf(p)
    elif ext == ".docx":
        text = _read_docx(p)
    elif ext in (".md", ".txt"):
        text = p.read_text(encoding="utf-8")
    else:
        raise SystemExit(f"Формат {ext} не поддерживается: PDF, DOCX, MD, TXT.")
    lines = text.splitlines()
    title = next((l.strip("# ").strip() for l in lines if l.strip()), p.name)
    return Document(path=str(p), title=title, lines=lines)
