"""Unit tests for CLI adapter — call run_cli() directly (no subprocess)."""

from pathlib import Path

from jano.cli.adapter import run_cli

TEST_CASE = Path(__file__).parent.parent.parent / "test-case"
DOCX_FILE = str(TEST_CASE / "Que es un LLM.docx")
MD_FILE = str(TEST_CASE / "Que es un LLM.md")


def test_help_flag(capsys):
    code = run_cli(["--help"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Usage" in out


def test_h_flag(capsys):
    code = run_cli(["-h"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Usage" in out


def test_no_args_shows_usage(capsys):
    code = run_cli([])
    out = capsys.readouterr().out
    assert code == 0
    assert "Usage" in out


def test_too_few_args_returns_1(capsys):
    code = run_cli(["only_one.docx"])
    err = capsys.readouterr().err
    assert code == 1
    assert "Error" in err


def test_docx_to_md_success(tmp_path, capsys):
    out = str(tmp_path / "out.md")
    code = run_cli([DOCX_FILE, out])
    stdout = capsys.readouterr().out
    assert code == 0
    assert "Converted" in stdout
    assert Path(out).exists()


def test_md_to_docx_success(tmp_path, capsys):
    out = str(tmp_path / "out.docx")
    code = run_cli([MD_FILE, out])
    stdout = capsys.readouterr().out
    assert code == 0
    assert "Converted" in stdout


def test_missing_file_returns_1(capsys):
    code = run_cli(["/nonexistent/file.docx", "/tmp/out.md"])
    err = capsys.readouterr().err
    assert code == 1
    assert "Error" in err


def test_bad_extension_returns_1(tmp_path, capsys):
    bad = tmp_path / "file.txt"
    bad.write_text("hello")
    code = run_cli([str(bad), str(tmp_path / "out.pdf")])
    err = capsys.readouterr().err
    assert code == 1
    assert "Error" in err


def test_unexpected_exception_returns_1(tmp_path, capsys, monkeypatch):
    from unittest.mock import patch

    with patch("jano.cli.adapter.convert_file", side_effect=RuntimeError("boom")):
        code = run_cli([DOCX_FILE, str(tmp_path / "out.md")])
    err = capsys.readouterr().err
    assert code == 1
    assert "Unexpected error" in err


def test_warnings_printed_to_stderr(tmp_path, capsys):
    md = tmp_path / "in.md"
    md.write_text("<div>html</div>\n", encoding="utf-8")
    out = str(tmp_path / "out.docx")
    code = run_cli([str(md), out])
    captured = capsys.readouterr()
    assert code == 0
    assert "[WARN]" in captured.err
