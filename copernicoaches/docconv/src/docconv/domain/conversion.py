"""
Main conversion functions for the domain layer.

This module provides the high-level conversion functions that
integrate DOCX-to-Markdown and Markdown-to-DOCX conversions.
"""

from .docx_to_md import docx_to_markdown
from .md_to_docx import markdown_to_docx
from .models import Document, ConversionWarning
from typing import List, Tuple


def convert_docx_to_markdown(document: Document) -> Tuple[str, List[ConversionWarning]]:
    """
    Convert a Document structure to Markdown text.

    This is a convenience function that wraps docx_to_markdown.

    Args:
        document: The document to convert

    Returns:
        Tuple of (markdown_text, warnings)
    """
    return docx_to_markdown(document)


def convert_markdown_to_docx(markdown_text: str) -> Tuple[Document, List[ConversionWarning]]:
    """
    Convert Markdown text to a Document structure.

    This is a convenience function that wraps markdown_to_docx.

    Args:
        markdown_text: The markdown text to convert

    Returns:
        Tuple of (document, warnings)
    """
    return markdown_to_docx(markdown_text)


__all__ = [
    "convert_docx_to_markdown",
    "convert_markdown_to_docx",
]