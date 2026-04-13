import subprocess
import sys
from pathlib import Path

JANO_PKG = Path(__file__).parent.parent.parent / "src" / "jano"
TEST_CASE = Path(__file__).parent.parent.parent / "test-case"
PYTHON = sys.executable


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, "-m", "jano", *args],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent.parent),
    )


def test_help():
    result = run("--help")
    assert result.returncode == 0
    assert "Usage" in result.stdout


def test_no_args():
    result = run()
    assert result.returncode == 0  # --help branch: no args prints usage
    assert "Usage" in result.stdout


def test_too_few_args():
    result = run("only_one.docx")
    assert result.returncode == 1
    assert "Error" in result.stderr


def test_docx_to_md(tmp_path):
    out = str(tmp_path / "out.md")
    result = run(str(TEST_CASE / "Que es un LLM.docx"), out)
    assert result.returncode == 0
    assert "Converted" in result.stdout
    assert Path(out).exists()
    assert Path(out).stat().st_size > 0


def test_md_to_docx(tmp_path):
    out = str(tmp_path / "out.docx")
    result = run(str(TEST_CASE / "Que es un LLM.md"), out)
    assert result.returncode == 0
    assert "Converted" in result.stdout
    assert Path(out).exists()
    assert Path(out).stat().st_size > 0


def test_missing_input_file(tmp_path):
    result = run("/nonexistent/file.docx", str(tmp_path / "out.md"))
    assert result.returncode == 1
    assert "Error" in result.stderr


def test_bad_extension(tmp_path):
    bad = tmp_path / "file.txt"
    bad.write_text("hello")
    result = run(str(bad), str(tmp_path / "out.pdf"))
    assert result.returncode == 1
