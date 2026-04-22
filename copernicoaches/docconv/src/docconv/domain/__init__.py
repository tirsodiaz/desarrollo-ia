"""
Domain layer for document conversion.

This package contains the pure business logic for converting between
Word (.docx) and Markdown (.md) formats, without any I/O dependencies.
"""

from .models import (
    Document,
    DocumentElement,
    Paragraph,
    Heading,
    DocumentList,
    ListItem,
    Table,
    TableRow,
    TableCell,
    Blockquote,
    CodeBlock,
    HorizontalRule,
    FormattedText,
    TextFormat,
    Link,
    ConversionWarning,
)

from .conversion import (
    convert_docx_to_markdown,
    convert_markdown_to_docx,
)

__all__ = [
    # Models
    "Document",
    "DocumentElement",
    "Paragraph",
    "Heading",
    "DocumentList",
    "ListItem",
    "Table",
    "TableRow",
    "TableCell",
    "Blockquote",
    "CodeBlock",
    "HorizontalRule",
    "FormattedText",
    "TextFormat",
    "Link",
    "ConversionWarning",
    # Conversion functions
    "convert_docx_to_markdown",
    "convert_markdown_to_docx",
]