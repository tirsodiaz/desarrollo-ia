"""Unit tests for MCP adapter — call convert_document() directly."""

from pathlib import Path

from jano.mcp.adapter import convert_document

TEST_CASE = Path(__file__).parent.parent.parent / "test-case"
DOCX_FILE = str(TEST_CASE / "Que es un LLM.docx")
MD_FILE = str(TEST_CASE / "Que es un LLM.md")


def test_convert_docx_to_md_success(tmp_path):
    out = str(tmp_path / "out.md")
    result = convert_document(DOCX_FILE, out)
    assert result["success"] is True
    assert result["error"] is None
    assert isinstance(result["warnings"], list)
    assert Path(out).exists()


def test_convert_md_to_docx_success(tmp_path):
    out = str(tmp_path / "out.docx")
    result = convert_document(MD_FILE, out)
    assert result["success"] is True
    assert result["error"] is None
    assert Path(out).exists()


def test_convert_missing_file_returns_error():
    result = convert_document("/nonexistent/file.docx", "/tmp/out.md")
    assert result["success"] is False
    assert result["error"] is not None
    assert isinstance(result["error"], str)


def test_convert_bad_extension(tmp_path):
    bad = tmp_path / "file.txt"
    bad.write_text("hello")
    result = convert_document(str(bad), str(tmp_path / "out.pdf"))
    assert result["success"] is False
    assert "Unsupported" in result["error"]


def test_warnings_serialized(tmp_path):
    md = tmp_path / "in.md"
    md.write_text("<div>html block</div>\n", encoding="utf-8")
    out = str(tmp_path / "out.docx")
    result = convert_document(str(md), out)
    assert result["success"] is True
    assert any(w["element_type"] == "raw_html" for w in result["warnings"])
