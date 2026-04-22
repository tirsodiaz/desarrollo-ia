"""
Infrastructure layer for document I/O operations.
"""

from .reader import read_docx, read_markdown
from .writer import write_docx, write_markdown

__all__ = [
    "read_docx",
    "read_markdown",
    "write_docx",
    "write_markdown",
]