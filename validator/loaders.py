"""Read an input document (PDF/DOCX/MD/TXT) into lines."""
import re
from pathlib import Path

from .models import Document


def _read_pdf(path: Path) -> str:
    import fitz  # pymupdf

    with fitz.open(path) as pdf:
        # sort=True: reading order by position; without it, PDFs that split text into runs
        # (e.g. exported from Word/LibreOffice) come out with words shuffled across lines
        text = "\n".join(page.get_text(sort=True) for page in pdf)
    return _tidy_pdf_text(text)


def _tidy_pdf_text(text: str) -> str:
    """Undo the spaces PDF export puts between text runs, so LLM quotes match the document:
    "Алматы ." -> "Алматы.", "Ф -2" -> "Ф-2", "версия /дата" -> "версия/дата"."""
    text = re.sub(r"[ \t]+([.,:;!?)\]»])", r"\1", text)
    text = re.sub(r"([(\[«])[ \t]+", r"\1", text)
    return re.sub(r"(?<=\w) ([-/])(?=\w)", r"\1", text)


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
