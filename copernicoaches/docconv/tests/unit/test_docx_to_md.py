"""
Unit tests for DOCX to Markdown conversion.
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
    convert_docx_to_markdown,
)


class TestDocxToMarkdownConversion:
    """Test DOCX to Markdown conversion functions."""

    def test_convert_paragraph(self):
        """Test paragraph conversion."""
        from docconv.domain.docx_to_md import convert_paragraph

        para = Paragraph(content=["Hello world"])
        result = convert_paragraph(para)
        assert result == "Hello world\n\n"

    def test_convert_heading(self):
        """Test heading conversion."""
        from docconv.domain.docx_to_md import convert_heading

        heading = Heading(level=1, content=["Title"])
        result = convert_heading(heading)
        assert result == "# Title\n\n"

        heading2 = Heading(level=2, content=["Subtitle"])
        result2 = convert_heading(heading2)
        assert result2 == "## Subtitle\n\n"

    def test_convert_formatted_text(self):
        """Test formatted text conversion."""
        from docconv.domain.docx_to_md import format_text_element

        # Bold text
        bold = FormattedText(text="bold", formats=[TextFormat.BOLD])
        result = format_text_element(bold)
        assert result == "**bold**"

        # Italic text
        italic = FormattedText(text="italic", formats=[TextFormat.ITALIC])
        result = format_text_element(italic)
        assert result == "*italic*"

        # Code text
        code = FormattedText(text="code", formats=[TextFormat.CODE])
        result = format_text_element(code)
        assert result == "`code`"

        # Link
        link = FormattedText(text="link", link=Link(text="link", url="https://example.com"))
        result = format_text_element(link)
        assert result == "[link](https://example.com)"

        # Multiple formats
        multi = FormattedText(text="text", formats=[TextFormat.BOLD, TextFormat.ITALIC])
        result = format_text_element(multi)
        assert result == "***text***"  # Bold and italic combine

    def test_convert_unordered_list(self):
        """Test unordered list conversion."""
        from docconv.domain.docx_to_md import convert_list

        list_obj = DocumentList(ordered=False, items=[
            ListItem(content=["Item 1"]),
            ListItem(content=["Item 2"])
        ])
        result = convert_list(list_obj)
        expected = "- Item 1\n- Item 2\n\n"
        assert result == expected

    def test_convert_ordered_list(self):
        """Test ordered list conversion."""
        from docconv.domain.docx_to_md import convert_list

        list_obj = DocumentList(ordered=True, items=[
            ListItem(content=["First"]),
            ListItem(content=["Second"])
        ])
        result = convert_list(list_obj)
        expected = "1. First\n2. Second\n\n"
        assert result == expected

    def test_convert_table(self):
        """Test table conversion."""
        from docconv.domain.docx_to_md import convert_table

        table = Table(
            headers=[TableRow(cells=[
                TableCell(content=["Header 1"]),
                TableCell(content=["Header 2"])
            ])],
            rows=[TableRow(cells=[
                TableCell(content=["Data 1"]),
                TableCell(content=["Data 2"])
            ])]
        )
        result = convert_table(table)
        expected = "| Header 1 | Header 2 |\n| --- | --- |\n| Data 1 | Data 2 |\n\n"
        assert result == expected

    def test_convert_blockquote(self):
        """Test blockquote conversion."""
        from docconv.domain.docx_to_md import convert_blockquote

        blockquote = Blockquote(content=["This is a quote"])
        result = convert_blockquote(blockquote)
        assert result == "> This is a quote\n\n"

    def test_convert_code_block(self):
        """Test code block conversion."""
        from docconv.domain.docx_to_md import convert_code_block

        code_block = CodeBlock(language="python", code="print('hello')")
        result = convert_code_block(code_block)
        expected = "```python\nprint('hello')\n```\n\n"
        assert result == expected

        # Without language
        code_block_no_lang = CodeBlock(code="print('hello')")
        result_no_lang = convert_code_block(code_block_no_lang)
        expected_no_lang = "```\nprint('hello')\n```\n\n"
        assert result_no_lang == expected_no_lang

    def test_convert_horizontal_rule(self):
        """Test horizontal rule conversion."""
        from docconv.domain.docx_to_md import convert_horizontal_rule

        hr = HorizontalRule()
        result = convert_horizontal_rule(hr)
        assert result == "---\n\n"

    def test_full_document_conversion(self):
        """Test full document conversion."""
        doc = Document(
            title="Test Document",
            elements=[
                Heading(level=1, content=["Main Title"]),
                Paragraph(content=["This is a paragraph."]),
                Heading(level=2, content=["Section"]),
                DocumentList(ordered=False, items=[
                    ListItem(content=["Bullet 1"]),
                    ListItem(content=["Bullet 2"])
                ]),
                CodeBlock(language="python", code="print('hello')"),
            ]
        )

        markdown, warnings = convert_docx_to_markdown(doc)

        expected_lines = [
            "# Main Title",
            "",
            "This is a paragraph.",
            "",
            "## Section",
            "",
            "- Bullet 1",
            "- Bullet 2",
            "",
            "```python",
            "print('hello')",
            "```"
        ]

        expected = "\n".join(expected_lines)
        # Allow for optional trailing newline
        assert markdown == expected or markdown == expected + "\n"
        assert warnings == []  # No warnings for supported elements

    def test_document_with_unsupported_element(self):
        """Test document with unsupported element generates warning."""
        # For this test, we'll mock the isinstance check to return an unknown type
        # This simulates what would happen if we had an element type not in DocumentElement union
        from unittest.mock import patch

        doc = Document(elements=[Paragraph(content=["test"])])

        # Mock isinstance to return False for all known types, simulating an unknown element
        with patch('docconv.domain.docx_to_md.isinstance') as mock_isinstance:
            def side_effect(obj, cls):
                # Return False for all our known element types, True for others
                known_types = (Paragraph, Heading, DocumentList, Table, Blockquote, CodeBlock, HorizontalRule)
                if cls in known_types:
                    return False
                return True  # For other type checks

            mock_isinstance.side_effect = side_effect

            markdown, warnings = convert_docx_to_markdown(doc)

            assert len(warnings) == 1
            assert "Unsupported element type" in warnings[0].description