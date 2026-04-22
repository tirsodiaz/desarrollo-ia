"""
Pure conversion from DOCX document structures to Markdown text.

This module implements the conversion logic from internal Document
representation to Markdown syntax, preserving structure and basic formatting.
"""

from typing import List, Optional, Union
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


def format_text_element(element: Union[str, FormattedText]) -> str:
    """Format a text element with its formatting applied."""
    if isinstance(element, str):
        return element

    text = element.text

    # Apply formatting in order: links, then text formats
    if element.link:
        return f"[{text}]({element.link.url})"

    for fmt in element.formats:
        if fmt == TextFormat.BOLD:
            text = f"**{text}**"
        elif fmt == TextFormat.ITALIC:
            text = f"*{text}*"
        elif fmt == TextFormat.CODE:
            text = f"`{text}`"
        elif fmt == TextFormat.STRIKETHROUGH:
            text = f"~~{text}~~"

    return text


def convert_paragraph(paragraph: Paragraph) -> str:
    """Convert a paragraph to Markdown."""
    if not paragraph.content:
        return ""

    content = "".join(format_text_element(elem) for elem in paragraph.content)
    return content + "\n\n"


def convert_heading(heading: Heading) -> str:
    """Convert a heading to Markdown."""
    if not heading.content:
        return ""

    level = "#" * heading.level
    content = "".join(format_text_element(elem) for elem in heading.content)
    return f"{level} {content}\n\n"


def convert_list_item(item: ListItem, ordered: bool, index: int = 1) -> str:
    """Convert a list item to Markdown."""
    if not item.content:
        return ""

    indent = "  " * (item.level - 1)
    marker = f"{index}." if ordered else "-"
    content = "".join(format_text_element(elem) for elem in item.content)
    return f"{indent}{marker} {content}\n"


def convert_list(list_obj: DocumentList) -> str:
    """Convert a list to Markdown."""
    if not list_obj.items:
        return ""

    result = ""
    for i, item in enumerate(list_obj.items, 1):
        result += convert_list_item(item, list_obj.ordered, i)
    return result + "\n"


def convert_table(table: Table) -> str:
    """Convert a table to Markdown."""
    if not table.rows:
        return ""

    # Build table content
    table_lines = []

    # Add header row if present
    if table.headers and table.headers:
        header_row = table.headers[0]  # Use first header row
        header_cells = []
        for cell in header_row.cells:
            content = "".join(format_text_element(elem) for elem in cell.content)
            header_cells.append(content)
        table_lines.append("| " + " | ".join(header_cells) + " |")

        # Add separator
        separators = ["---"] * len(header_cells)
        table_lines.append("| " + " | ".join(separators) + " |")

    # Add data rows
    for row in table.rows:
        cells = []
        for cell in row.cells:
            content = "".join(format_text_element(elem) for elem in cell.content)
            cells.append(content)
        table_lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(table_lines) + "\n\n"


def convert_blockquote(blockquote: Blockquote) -> str:
    """Convert a blockquote to Markdown."""
    if not blockquote.content:
        return ""

    content = "".join(format_text_element(elem) for elem in blockquote.content)
    # Split into lines and add > prefix
    lines = content.split("\n")
    quoted_lines = [f"> {line}" if line.strip() else ">" for line in lines]
    return "\n".join(quoted_lines) + "\n\n"


def convert_code_block(code_block: CodeBlock) -> str:
    """Convert a code block to Markdown."""
    if not code_block.code:
        return ""

    if code_block.language:
        return f"```{code_block.language}\n{code_block.code}\n```\n\n"
    else:
        return f"```\n{code_block.code}\n```\n\n"


def convert_horizontal_rule(hr: HorizontalRule) -> str:
    """Convert a horizontal rule to Markdown."""
    return "---\n\n"


def docx_to_markdown(document: Document) -> tuple[str, List[ConversionWarning]]:
    """
    Convert a Document structure to Markdown text.

    Args:
        document: The document to convert

    Returns:
        Tuple of (markdown_text, warnings_list)
    """
    warnings: List[ConversionWarning] = []
    markdown_parts: List[str] = []

    # Note: Document title is not converted to markdown heading
    # to maintain clean round-trip conversion. Title is metadata only.

    # Convert each element
    for element in document.elements:
        if isinstance(element, Paragraph):
            markdown_parts.append(convert_paragraph(element))
        elif isinstance(element, Heading):
            markdown_parts.append(convert_heading(element))
        elif isinstance(element, DocumentList):
            markdown_parts.append(convert_list(element))
        elif isinstance(element, Table):
            markdown_parts.append(convert_table(element))
        elif isinstance(element, Blockquote):
            markdown_parts.append(convert_blockquote(element))
        elif isinstance(element, CodeBlock):
            markdown_parts.append(convert_code_block(element))
        elif isinstance(element, HorizontalRule):
            markdown_parts.append(convert_horizontal_rule(element))
        else:
            # Unknown element type - add warning
            warnings.append(ConversionWarning(
                element_type=type(element).__name__,
                description=f"Unsupported element type: {type(element).__name__}",
                details={"element": str(element)}
            ))

    # Join all parts
    markdown_text = "".join(markdown_parts)

    # Clean up excessive newlines
    import re
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)

    return markdown_text.strip(), warnings