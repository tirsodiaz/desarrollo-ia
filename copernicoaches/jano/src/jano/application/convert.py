from pathlib import Path

from jano.domain.docx_to_md import convert_docx_to_md
from jano.domain.md_to_docx import convert_md_to_docx
from jano.domain.models import ConversionResult
from jano.infrastructure.reader import read_docx, read_md
from jano.infrastructure.writer import write_docx, write_md


def convert_file(input_path: str, output_path: str) -> ConversionResult:
    in_ext = Path(input_path).suffix.lower()
    out_ext = Path(output_path).suffix.lower()

    if in_ext == ".docx" and out_ext == ".md":
        document = read_docx(input_path)
        result = convert_docx_to_md(document)
        assert isinstance(result.content, str)
        write_md(result.content, output_path)
        return result

    if in_ext == ".md" and out_ext == ".docx":
        text = read_md(input_path)
        result = convert_md_to_docx(text)
        assert isinstance(result.content, bytes)
        write_docx(result.content, output_path)
        return result

    raise ValueError(
        f"Unsupported conversion: {in_ext} → {out_ext}. "
        "Supported: .docx → .md, .md → .docx"
    )
