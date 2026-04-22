"""
Pure conversion from Markdown text to DOCX document structures.

This module implements the conversion logic from Markdown syntax to
internal Document representation, preserving structure and basic formatting.
"""

import re
from typing import List, Optional, Tuple, Union
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


def parse_formatted_text(text: str) -> List[Union[str, FormattedText]]:
    """
    Parse text with Markdown formatting into a list of text elements.

    Handles: **bold**, *italic*, `code`, ~~strikethrough~~, [links](url)
    """
    elements: List[Union[str, FormattedText]] = []

    # Process links first: [text](url)
    while '[' in text and '](' in text and ')' in text:
        # Find link
        match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', text)
        if not match:
            break

        # Add text before link
        before = text[:match.start()]
        if before:
            elements.extend(parse_simple_formats(before))

        # Add link
        link_text = match.group(1)
        url = match.group(2)
        elements.append(FormattedText(
            text=link_text,
            link=Link(text=link_text, url=url)
        ))

        # Continue with text after link
        text = text[match.end():]

    # Process remaining text with simple formats
    if text:
        elements.extend(parse_simple_formats(text))

    return elements


def parse_simple_formats(text: str) -> List[Union[str, FormattedText]]:
    """Parse simple formats: **bold**, *italic*, `code`, ~~strikethrough~~"""
    elements: List[Union[str, FormattedText]] = []

    # Split by format markers
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`|~~.*?~~)', text)

    for part in parts:
        if not part:  # Skip empty strings
            continue

        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            # Bold
            content = part[2:-2]
            elements.append(FormattedText(text=content, formats=[TextFormat.BOLD]))
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            # Italic
            content = part[1:-1]
            elements.append(FormattedText(text=content, formats=[TextFormat.ITALIC]))
        elif part.startswith('`') and part.endswith('`') and len(part) > 2:
            # Code
            content = part[1:-1]
            elements.append(FormattedText(text=content, formats=[TextFormat.CODE]))
        elif part.startswith('~~') and part.endswith('~~') and len(part) > 4:
            # Strikethrough
            content = part[2:-2]
            elements.append(FormattedText(text=content, formats=[TextFormat.STRIKETHROUGH]))
        else:
            # Plain text
            elements.append(part)

    return elements


def parse_heading(line: str) -> Optional[Heading]:
    """Parse a heading line like '# Title' or '## Subtitle'."""
    match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
    if match:
        level = len(match.group(1))
        content = parse_formatted_text(match.group(2))
        return Heading(level=level, content=content)
    return None


def parse_code_block(lines: List[str], start_idx: int) -> Tuple[Optional[CodeBlock], int]:
    """Parse a code block starting at the given line index."""
    if start_idx >= len(lines) or not lines[start_idx].startswith('```'):
        return None, start_idx

    # Extract language if present
    first_line = lines[start_idx].strip()
    language = None
    if len(first_line) > 3:
        language = first_line[3:].strip()

    # Find the closing ```
    code_lines = []
    idx = start_idx + 1
    while idx < len(lines):
        if lines[idx].strip() == '```':
            break
        code_lines.append(lines[idx])
        idx += 1

    if idx < len(lines):  # Found closing ```
        code = '\n'.join(code_lines)
        return CodeBlock(language=language, code=code), idx + 1
    else:
        # Unclosed code block - treat as regular text
        return None, start_idx


def parse_table(lines: List[str], start_idx: int) -> Tuple[Optional[Table], int]:
    """Parse a table starting at the given line index."""
    if start_idx + 1 >= len(lines):
        return None, start_idx

    # Check if we have a header and separator
    header_line = lines[start_idx].strip()
    separator_line = lines[start_idx + 1].strip()

    if not (header_line.startswith('|') and header_line.endswith('|') and
            separator_line.startswith('|') and separator_line.endswith('|')):
        return None, start_idx

    # Parse header
    header_cells = [cell.strip() for cell in header_line.split('|')[1:-1]]
    header_row = TableRow(cells=[
        TableCell(content=parse_formatted_text(cell)) for cell in header_cells
    ])

    # Parse data rows
    data_rows = []
    idx = start_idx + 2
    while idx < len(lines):
        line = lines[idx].strip()
        if not (line.startswith('|') and line.endswith('|')):
            break

        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        data_rows.append(TableRow(cells=[
            TableCell(content=parse_formatted_text(cell)) for cell in cells
        ]))
        idx += 1

    return Table(headers=[header_row], rows=data_rows), idx


def parse_list(lines: List[str], start_idx: int) -> Tuple[Optional[DocumentList], int]:
    """Parse a list starting at the given line index."""
    if start_idx >= len(lines):
        return None, start_idx

    first_line = lines[start_idx].strip()

    # Check if it's a list item
    ordered_match = re.match(r'^(\d+)\.\s+(.+)$', first_line)
    unordered_match = re.match(r'^-\s+(.+)$', first_line)

    if not (ordered_match or unordered_match):
        return None, start_idx

    ordered = ordered_match is not None
    items = []
    idx = start_idx

    while idx < len(lines):
        line = lines[idx].strip()

        if ordered:
            match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if not match:
                # Check if this is an empty line that ends the list
                if line == "" and items:  # Empty line after items
                    idx += 1  # Consume the empty line
                break
            content = match.group(2)
        else:
            match = re.match(r'^-\s+(.+)$', line)
            if not match:
                # Check if this is an empty line that ends the list
                if line == "" and items:  # Empty line after items
                    idx += 1  # Consume the empty line
                break
            content = match.group(1)

        # Check indentation for nested lists (simplified)
        level = 1
        if lines[idx].startswith('  '):
            level = 2
        if lines[idx].startswith('    '):
            level = 3

        items.append(ListItem(content=parse_formatted_text(content), level=level))
        idx += 1

    return DocumentList(ordered=ordered, items=items), idx


def parse_blockquote(lines: List[str], start_idx: int) -> Tuple[Optional[Blockquote], int]:
    """Parse a blockquote starting at the given line index."""
    if start_idx >= len(lines) or not lines[start_idx].strip().startswith('>'):
        return None, start_idx

    content_lines = []
    idx = start_idx

    while idx < len(lines):
        line = lines[idx].strip()
        if not line.startswith('>'):
            # Check if this is an empty line that ends the blockquote
            if line == "" and content_lines:  # Empty line after content
                idx += 1  # Consume the empty line
            break

        # Remove the > prefix and any following space
        if line.startswith('> '):
            content_lines.append(line[2:])
        elif line == '>':
            content_lines.append('')
        else:
            break

        idx += 1

    if content_lines:
        content = ' '.join(content_lines)  # Join with spaces, not newlines
        return Blockquote(content=parse_formatted_text(content)), idx

    return None, start_idx


def markdown_to_docx(markdown_text: str) -> tuple[Document, List[ConversionWarning]]:
    """
    Convert Markdown text to a Document structure.

    Args:
        markdown_text: The markdown text to convert

    Returns:
        Tuple of (document, warnings_list)
    """
    warnings: List[ConversionWarning] = []
    elements: List[DocumentElement] = []

    lines = markdown_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines at the beginning of processing
        if not line.strip():
            i += 1
            continue

        # Try to parse different element types
        element = None
        consumed_lines = 1

        # Check for headings
        heading = parse_heading(line)
        if heading:
            element = heading

        # Check for horizontal rules
        elif line.strip() in ['---', '***', '___']:
            element = HorizontalRule()

        # Check for code blocks
        elif line.strip().startswith('```'):
            code_block, new_i = parse_code_block(lines, i)
            if code_block:
                element = code_block
                consumed_lines = new_i - i

        # Check for tables
        elif line.strip().startswith('|'):
            table, new_i = parse_table(lines, i)
            if table:
                element = table
                consumed_lines = new_i - i

        # Check for lists
        elif re.match(r'^(\d+\.|-)\s', line.strip()):
            list_obj, new_i = parse_list(lines, i)
            if list_obj:
                element = list_obj
                consumed_lines = new_i - i

        # Check for blockquotes
        elif line.strip().startswith('>'):
            blockquote, new_i = parse_blockquote(lines, i)
            if blockquote:
                element = blockquote
                consumed_lines = new_i - i

        # Default to paragraph
        else:
            # Collect consecutive non-empty lines as a paragraph
            para_lines = []
            j = i
            while j < len(lines):
                current_line = lines[j]
                if not current_line.strip():
                    break
                # Check if next line starts a new element
                if (j + 1 < len(lines) and
                    (parse_heading(lines[j + 1]) or
                     lines[j + 1].strip() in ['---', '***', '___'] or
                     lines[j + 1].strip().startswith('```') or
                     lines[j + 1].strip().startswith('|') or
                     re.match(r'^(\d+\.|-)\s', lines[j + 1].strip()) or
                     lines[j + 1].strip().startswith('>'))):
                    break
                para_lines.append(current_line)
                j += 1

            if para_lines:
                content = ' '.join(line.strip() for line in para_lines)
                element = Paragraph(content=parse_formatted_text(content))
                consumed_lines = j - i

        if element:
            elements.append(element)

        i += consumed_lines

    # Create document
    document = Document(elements=elements)

    return document, warnings