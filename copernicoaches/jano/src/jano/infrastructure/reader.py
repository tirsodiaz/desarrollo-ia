from pathlib import Path

from docx import Document


def read_docx(path: str) -> Document:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if p.suffix.lower() != ".docx":
        raise ValueError(f"Expected .docx file, got: {p.suffix}")
    return Document(str(p))


def read_md(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if p.suffix.lower() != ".md":
        raise ValueError(f"Expected .md file, got: {p.suffix}")
    return p.read_text(encoding="utf-8")
