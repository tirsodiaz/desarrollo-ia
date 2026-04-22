"""
Unit tests for domain models.
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
    ConversionWarning,
)


class TestFormattedText:
    """Test FormattedText model."""

    def test_plain_text(self):
        """Test plain text without formatting."""
        text = FormattedText(text="Hello world")
        assert text.text == "Hello world"
        assert text.formats == []
        assert text.link is None

    def test_bold_text(self):
        """Test bold formatted text."""
        text = FormattedText(text="bold", formats=[TextFormat.BOLD])
        assert text.text == "bold"
        assert text.formats == [TextFormat.BOLD]

    def test_multiple_formats(self):
        """Test text with multiple formats."""
        text = FormattedText(
            text="formatted",
            formats=[TextFormat.BOLD, TextFormat.ITALIC]
        )
        assert text.formats == [TextFormat.BOLD, TextFormat.ITALIC]

    def test_text_with_link(self):
        """Test text with hyperlink."""
        link = Link(text="click here", url="https://example.com")
        text = FormattedText(text="click here", link=link)
        assert text.link == link
        assert text.link.url == "https://example.com"


class TestParagraph:
    """Test Paragraph model."""

    def test_empty_paragraph(self):
        """Test empty paragraph."""
        para = Paragraph()
        assert para.content == []

    def test_paragraph_with_text(self):
        """Test paragraph with plain text."""
        para = Paragraph(content=["Hello world"])
        assert para.content == ["Hello world"]

    def test_paragraph_with_formatted_text(self):
        """Test paragraph with formatted text."""
        formatted = FormattedText(text="bold", formats=[TextFormat.BOLD])
        para = Paragraph(content=["Hello ", formatted, " world"])
        assert len(para.content) == 3
        assert para.content[1] == formatted


class TestHeading:
    """Test Heading model."""

    def test_h1_heading(self):
        """Test H1 heading."""
        heading = Heading(level=1, content=["Title"])
        assert heading.level == 1
        assert heading.content == ["Title"]

    def test_invalid_heading_level(self):
        """Test that invalid heading levels raise validation errors."""
        with pytest.raises(ValueError):
            Heading(level=0, content=["Invalid"])

        with pytest.raises(ValueError):
            Heading(level=7, content=["Invalid"])


class TestList:
    """Test DocumentList model."""

    def test_unordered_list(self):
        """Test unordered list."""
        list_obj = DocumentList(ordered=False, items=[
            ListItem(content=["Item 1"]),
            ListItem(content=["Item 2"])
        ])
        assert not list_obj.ordered
        assert len(list_obj.items) == 2

    def test_ordered_list(self):
        """Test ordered list."""
        list_obj = DocumentList(ordered=True, items=[
            ListItem(content=["First"]),
            ListItem(content=["Second"])
        ])
        assert list_obj.ordered
        assert len(list_obj.items) == 2

    def test_nested_list_item(self):
        """Test nested list item."""
        item = ListItem(content=["Nested item"], level=2)
        assert item.level == 2


class TestTable:
    """Test Table model."""

    def test_simple_table(self):
        """Test simple table without headers."""
        table = Table(rows=[
            TableRow(cells=[
                TableCell(content=["Cell 1"]),
                TableCell(content=["Cell 2"])
            ])
        ])
        assert len(table.rows) == 1
        assert table.headers is None

    def test_table_with_headers(self):
        """Test table with headers."""
        headers = [TableRow(cells=[
            TableCell(content=["Header 1"]),
            TableCell(content=["Header 2"])
        ])]

        rows = [TableRow(cells=[
            TableCell(content=["Data 1"]),
            TableCell(content=["Data 2"])
        ])]

        table = Table(headers=headers, rows=rows)
        assert table.headers == headers
        assert table.rows == rows


class TestCodeBlock:
    """Test CodeBlock model."""

    def test_code_block_with_language(self):
        """Test code block with language specification."""
        code = CodeBlock(language="python", code="print('hello')")
        assert code.language == "python"
        assert code.code == "print('hello')"

    def test_code_block_without_language(self):
        """Test code block without language."""
        code = CodeBlock(code="print('hello')")
        assert code.language is None
        assert code.code == "print('hello')"


class TestDocument:
    """Test Document model."""

    def test_empty_document(self):
        """Test empty document."""
        doc = Document()
        assert doc.title is None
        assert doc.elements == []

    def test_document_with_title(self):
        """Test document with title."""
        doc = Document(title="My Document")
        assert doc.title == "My Document"

    def test_document_with_elements(self):
        """Test document with various elements."""
        elements = [
            Heading(level=1, content=["Title"]),
            Paragraph(content=["Content"])
        ]
        doc = Document(elements=elements)
        assert len(doc.elements) == 2


class TestConversionWarning:
    """Test ConversionWarning model."""

    def test_basic_warning(self):
        """Test basic conversion warning."""
        warning = ConversionWarning(
            element_type="image",
            description="Images are not supported"
        )
        assert warning.element_type == "image"
        assert warning.description == "Images are not supported"
        assert warning.position is None
        assert warning.details is None

    def test_warning_with_details(self):
        """Test warning with additional details."""
        warning = ConversionWarning(
            element_type="table",
            description="Complex table detected",
            position=5,
            details={"rows": 10, "columns": 5}
        )
        assert warning.position == 5
        assert warning.details == {"rows": 10, "columns": 5}