"""
Unit tests for Markdown to DOCX conversion.
"""

import pytest
from docconv.domain import (
    Document,
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
    convert_markdown_to_docx,
)


class TestMarkdownToDocxConversion:
    """Test Markdown to DOCX conversion functions."""

    def test_parse_formatted_text_plain(self):
        """Test parsing plain text."""
        from docconv.domain.md_to_docx import parse_formatted_text

        result = parse_formatted_text("Hello world")
        assert result == ["Hello world"]

    def test_parse_formatted_text_bold(self):
        """Test parsing bold text."""
        from docconv.domain.md_to_docx import parse_formatted_text

        result = parse_formatted_text("**bold text**")
        assert len(result) == 1
        assert isinstance(result[0], FormattedText)
        assert result[0].text == "bold text"
        assert result[0].formats == [TextFormat.BOLD]

    def test_parse_formatted_text_italic(self):
        """Test parsing italic text."""
        from docconv.domain.md_to_docx import parse_formatted_text

        result = parse_formatted_text("*italic text*")
        assert len(result) == 1
        assert isinstance(result[0], FormattedText)
        assert result[0].text == "italic text"
        assert result[0].formats == [TextFormat.ITALIC]

    def test_parse_formatted_text_code(self):
        """Test parsing inline code."""
        from docconv.domain.md_to_docx import parse_formatted_text

        result = parse_formatted_text("`code text`")
        assert len(result) == 1
        assert isinstance(result[0], FormattedText)
        assert result[0].text == "code text"
        assert result[0].formats == [TextFormat.CODE]

    def test_parse_formatted_text_link(self):
        """Test parsing links."""
        from docconv.domain.md_to_docx import parse_formatted_text

        result = parse_formatted_text("[link text](https://example.com)")
        assert len(result) == 1
        assert isinstance(result[0], FormattedText)
        assert result[0].text == "link text"
        assert result[0].link.url == "https://example.com"

    def test_parse_formatted_text_mixed(self):
        """Test parsing mixed formatted text."""
        from docconv.domain.md_to_docx import parse_formatted_text

        result = parse_formatted_text("Plain **bold** and *italic* text")
        assert len(result) == 5
        assert result[0] == "Plain "
        assert isinstance(result[1], FormattedText)
        assert result[1].text == "bold"
        assert result[1].formats == [TextFormat.BOLD]
        assert result[2] == " and "
        assert isinstance(result[3], FormattedText)
        assert result[3].text == "italic"
        assert result[3].formats == [TextFormat.ITALIC]
        assert result[4] == " text"

    def test_parse_heading(self):
        """Test parsing headings."""
        from docconv.domain.md_to_docx import parse_heading

        # H1
        result = parse_heading("# Main Title")
        assert result is not None
        assert result.level == 1
        assert result.content == ["Main Title"]

        # H2
        result = parse_heading("## Subtitle")
        assert result is not None
        assert result.level == 2
        assert result.content == ["Subtitle"]

        # Invalid
        result = parse_heading("Not a heading")
        assert result is None

    def test_parse_code_block(self):
        """Test parsing code blocks."""
        from docconv.domain.md_to_docx import parse_code_block

        lines = [
            "```python",
            "print('hello')",
            "print('world')",
            "```",
            "next line"
        ]

        result, new_idx = parse_code_block(lines, 0)
        assert result is not None
        assert result.language == "python"
        assert result.code == "print('hello')\nprint('world')"
        assert new_idx == 4

        # Without language
        lines2 = ["```", "code", "```"]
        result2, new_idx2 = parse_code_block(lines2, 0)
        assert result2 is not None
        assert result2.language is None
        assert result2.code == "code"

    def test_parse_table(self):
        """Test parsing tables."""
        from docconv.domain.md_to_docx import parse_table

        lines = [
            "| Header 1 | Header 2 |",
            "| --- | --- |",
            "| Data 1 | Data 2 |",
            "| Data 3 | Data 4 |",
            "",  # Empty line ends table
            "next content"
        ]

        result, new_idx = parse_table(lines, 0)
        assert result is not None
        assert len(result.headers) == 1
        assert len(result.rows) == 2
        assert new_idx == 4

    def test_parse_unordered_list(self):
        """Test parsing unordered lists."""
        from docconv.domain.md_to_docx import parse_list

        lines = [
            "- Item 1",
            "- Item 2",
            "",  # Empty line ends list
            "next content"
        ]

        result, new_idx = parse_list(lines, 0)
        assert result is not None
        assert not result.ordered
        assert len(result.items) == 2
        assert result.items[0].content == ["Item 1"]
        assert new_idx == 3

    def test_parse_ordered_list(self):
        """Test parsing ordered lists."""
        from docconv.domain.md_to_docx import parse_list

        lines = [
            "1. First item",
            "2. Second item",
            "",  # Empty line ends list
        ]

        result, new_idx = parse_list(lines, 0)
        assert result is not None
        assert result.ordered
        assert len(result.items) == 2
        assert result.items[0].content == ["First item"]
        assert new_idx == 3

    def test_parse_blockquote(self):
        """Test parsing blockquotes."""
        from docconv.domain.md_to_docx import parse_blockquote

        lines = [
            "> This is a quote",
            "> that spans multiple lines",
            "",  # Empty line ends blockquote
            "next content"
        ]

        result, new_idx = parse_blockquote(lines, 0)
        assert result is not None
        assert result.content == ["This is a quote that spans multiple lines"]
        assert new_idx == 3

    def test_full_markdown_conversion(self):
        """Test full markdown to document conversion."""
        markdown = """# Main Title

This is a paragraph with **bold** and *italic* text.

## Section

- Bullet 1
- Bullet 2

```python
print("hello world")
```

> This is a blockquote
"""

        document, warnings = convert_markdown_to_docx(markdown)

        assert len(document.elements) == 6

        # Check title (should be first heading)
        assert isinstance(document.elements[0], Heading)
        assert document.elements[0].level == 1
        assert document.elements[0].content == ["Main Title"]

        # Check paragraph
        assert isinstance(document.elements[1], Paragraph)

        # Check section heading
        assert isinstance(document.elements[2], Heading)
        assert document.elements[2].level == 2

        # Check list
        assert isinstance(document.elements[3], DocumentList)
        assert not document.elements[3].ordered
        assert len(document.elements[3].items) == 2

        # Check code block
        assert isinstance(document.elements[4], CodeBlock)
        assert document.elements[4].language == "python"

        # Check blockquote
        assert isinstance(document.elements[5], Blockquote)
        assert document.elements[5].content == ["This is a blockquote"]

        assert warnings == []

    def test_markdown_with_table(self):
        """Test markdown with table conversion."""
        markdown = """| Name | Age |
|------|-----|
| John | 25  |
| Jane | 30  |
"""

        document, warnings = convert_markdown_to_docx(markdown)

        assert len(document.elements) == 1
        assert isinstance(document.elements[0], Table)
        table = document.elements[0]
        assert len(table.headers) == 1
        assert len(table.rows) == 2
        assert warnings == []