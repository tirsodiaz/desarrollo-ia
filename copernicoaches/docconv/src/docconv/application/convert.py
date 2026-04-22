"""
Application layer for document conversion orchestration.

This module provides the main entry point for converting documents
between formats, coordinating domain and infrastructure layers.
"""

import os
from typing import Optional, List
from pathlib import Path

from ..domain.models import ConversionWarning
from ..infrastructure import read_docx, read_markdown, write_docx, write_markdown


class ConversionResult:
    """Result of a document conversion operation."""

    def __init__(
        self,
        success: bool,
        input_path: str,
        output_path: str,
        warnings: Optional[List[ConversionWarning]] = None,
        error_message: Optional[str] = None
    ):
        self.success = success
        self.input_path = input_path
        self.output_path = output_path
        self.warnings = warnings or []
        self.error_message = error_message

    def __repr__(self) -> str:
        return f"ConversionResult(success={self.success}, input={self.input_path}, output={self.output_path}, warnings={len(self.warnings)})"


def convert_file(input_path: str, output_path: str) -> ConversionResult:
    """
    Convert a document file from one format to another.

    Automatically determines conversion direction based on file extensions:
    - .docx -> .md
    - .md -> .docx

    Args:
        input_path: Path to the input file
        output_path: Path to write the output file

    Returns:
        ConversionResult with success status and any warnings/errors
    """
    # Validate input file exists
    if not os.path.exists(input_path):
        return ConversionResult(
            success=False,
            input_path=input_path,
            output_path=output_path,
            error_message=f"Input file does not exist: {input_path}"
        )

    # Determine conversion direction
    input_ext = Path(input_path).suffix.lower()
    output_ext = Path(output_path).suffix.lower()

    if input_ext == '.docx' and output_ext == '.md':
        # DOCX to Markdown
        return _convert_docx_to_markdown(input_path, output_path)
    elif input_ext == '.md' and output_ext == '.docx':
        # Markdown to DOCX
        return _convert_markdown_to_docx(input_path, output_path)
    else:
        return ConversionResult(
            success=False,
            input_path=input_path,
            output_path=output_path,
            error_message=f"Unsupported conversion: {input_ext} -> {output_ext}. Supported: .docx->.md, .md->.docx"
        )


def _convert_docx_to_markdown(input_path: str, output_path: str) -> ConversionResult:
    """Convert DOCX file to Markdown."""
    # Read DOCX
    document, read_warnings = read_docx(input_path)
    if document is None:
        return ConversionResult(
            success=False,
            input_path=input_path,
            output_path=output_path,
            warnings=read_warnings,
            error_message="Failed to read DOCX file"
        )

    # Convert to Markdown
    from ..domain.docx_to_md import docx_to_markdown
    markdown_text, conversion_warnings = docx_to_markdown(document)

    # Combine warnings
    all_warnings = read_warnings + conversion_warnings

    # Write Markdown file
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
    except Exception as e:
        return ConversionResult(
            success=False,
            input_path=input_path,
            output_path=output_path,
            warnings=all_warnings,
            error_message=f"Failed to write Markdown file: {str(e)}"
        )

    return ConversionResult(
        success=True,
        input_path=input_path,
        output_path=output_path,
        warnings=all_warnings
    )


def _convert_markdown_to_docx(input_path: str, output_path: str) -> ConversionResult:
    """Convert Markdown file to DOCX."""
    # Read Markdown
    document, read_warnings = read_markdown(input_path)
    if document is None:
        return ConversionResult(
            success=False,
            input_path=input_path,
            output_path=output_path,
            warnings=read_warnings,
            error_message="Failed to read Markdown file"
        )

    # Write DOCX file
    write_warnings = write_docx(document, output_path)

    # Combine warnings
    all_warnings = read_warnings + write_warnings

    # Check if write was successful (no error warnings)
    write_errors = [w for w in write_warnings if w.element_type == "file" and "Failed to write" in w.description]
    if write_errors:
        return ConversionResult(
            success=False,
            input_path=input_path,
            output_path=output_path,
            warnings=all_warnings,
            error_message="Failed to write DOCX file"
        )

    return ConversionResult(
        success=True,
        input_path=input_path,
        output_path=output_path,
        warnings=all_warnings
    )