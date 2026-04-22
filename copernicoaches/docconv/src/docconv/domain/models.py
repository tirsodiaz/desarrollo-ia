"""
Domain models for document conversion.

This module defines the core data structures used in the domain layer
for representing documents in a format-independent way.
"""

from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class TextFormat(str, Enum):
    """Text formatting options."""
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    STRIKETHROUGH = "strikethrough"


class Link(BaseModel):
    """Represents a hyperlink."""
    text: str
    url: str


class FormattedText(BaseModel):
    """Represents text with formatting and links."""
    text: str
    formats: List[TextFormat] = Field(default_factory=list)
    link: Optional[Link] = None


class Paragraph(BaseModel):
    """Represents a paragraph of text."""
    content: List[Union[str, FormattedText]] = Field(default_factory=list)


class Heading(BaseModel):
    """Represents a heading."""
    level: int = Field(ge=1, le=6)  # H1 to H6
    content: List[Union[str, FormattedText]] = Field(default_factory=list)


class ListItem(BaseModel):
    """Represents a list item."""
    content: List[Union[str, FormattedText]] = Field(default_factory=list)
    level: int = Field(default=1, ge=1)  # Nesting level


class DocumentList(BaseModel):
    """Represents a list (ordered or unordered)."""
    ordered: bool = False
    items: List[ListItem] = Field(default_factory=list)


class TableCell(BaseModel):
    """Represents a table cell."""
    content: List[Union[str, FormattedText]] = Field(default_factory=list)


class TableRow(BaseModel):
    """Represents a table row."""
    cells: List[TableCell] = Field(default_factory=list)


class Table(BaseModel):
    """Represents a table."""
    headers: Optional[List[TableRow]] = None
    rows: List[TableRow] = Field(default_factory=list)


class Blockquote(BaseModel):
    """Represents a blockquote."""
    content: List[Union[str, FormattedText]] = Field(default_factory=list)


class CodeBlock(BaseModel):
    """Represents a code block."""
    language: Optional[str] = None
    code: str


class HorizontalRule(BaseModel):
    """Represents a horizontal rule/thematic break."""
    pass


# Union type for all document elements
DocumentElement = Union[
    Paragraph,
    Heading,
    DocumentList,
    Table,
    Blockquote,
    CodeBlock,
    HorizontalRule
]


class Document(BaseModel):
    """Represents a complete document."""
    title: Optional[str] = None
    elements: List[DocumentElement] = Field(default_factory=list)


class ConversionWarning(BaseModel):
    """Represents a warning about unsupported or degraded elements during conversion."""
    element_type: str  # e.g., "image", "html", "complex_table"
    description: str   # Human-readable description
    position: Optional[int] = None  # Position in document (if applicable)
    details: Optional[Dict[str, Any]] = None  # Additional context