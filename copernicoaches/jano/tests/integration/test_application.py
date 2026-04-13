from pathlib import Path

import pytest
from docx import Document

from jano.application.convert import convert_file

TEST_CASE = Path(__file__).parent.parent.parent / "test-case"
DOCX_FILE = str(TEST_CASE / "Que es un LLM.docx")
MD_FILE = str(TEST_CASE / "Que es un LLM.md")


def test_docx_to_md(tmp_path):
    out = str(tmp_path / "out.md")
    convert_file(DOCX_FILE, out)
    assert Path(out).exists()
    content = Path(out).read_text(encoding="utf-8")
    assert len(content) > 100
    assert "#" in content  # has headings


def test_md_to_docx(tmp_path):
    out = str(tmp_path / "out.docx")
    convert_file(MD_FILE, out)
    assert Path(out).exists()
    doc = Document(out)
    headings = [p for p in doc.paragraphs if "Heading" in p.style.name]
    assert len(headings) > 0


def test_unsupported_extension(tmp_path):
    with pytest.raises(ValueError):
        convert_file(str(tmp_path / "file.txt"), str(tmp_path / "out.pdf"))


def test_warnings_passed_through(tmp_path):
    # MD → DOCX with HTML triggers a warning
    md = str(tmp_path / "in.md")
    Path(md).write_text("<div>raw html</div>\n", encoding="utf-8")
    out = str(tmp_path / "out.docx")
    result = convert_file(md, out)
    assert any(w.element_type == "raw_html" for w in result.warnings)
