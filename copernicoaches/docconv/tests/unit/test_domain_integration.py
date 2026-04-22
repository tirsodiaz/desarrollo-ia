"""
Integration tests for domain layer conversions.
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
    convert_markdown_to_docx,
)


class TestDomainIntegration:
    """Integration tests for domain layer."""

    def test_round_trip_simple_document(self):
        """Test round-trip conversion: DOCX -> MD -> DOCX."""
        # Create original document
        original_doc = Document(
            title="Test Document",
            elements=[
                Heading(level=1, content=["Main Title"]),
                Paragraph(content=["This is a simple paragraph."]),
                Heading(level=2, content=["Section"]),
                Paragraph(content=["Another paragraph with ", FormattedText(text="bold", formats=[TextFormat.BOLD]), " text."]),
            ]
        )

        # Convert to markdown
        markdown, warnings1 = convert_docx_to_markdown(original_doc)
        assert warnings1 == []

        # Convert back to document
        converted_doc, warnings2 = convert_markdown_to_docx(markdown)
        assert warnings2 == []

        # Verify structure is preserved (title is not converted to heading)
        assert converted_doc.title is None  # Title is not preserved in round-trip
        assert len(converted_doc.elements) == len(original_doc.elements)

        # Check headings
        assert isinstance(converted_doc.elements[0], Heading)
        assert converted_doc.elements[0].level == 1
        assert converted_doc.elements[0].content == ["Main Title"]

        assert isinstance(converted_doc.elements[2], Heading)
        assert converted_doc.elements[2].level == 2
        assert converted_doc.elements[2].content == ["Section"]

    def test_round_trip_with_list(self):
        """Test round-trip with lists."""
        original_doc = Document(elements=[
            DocumentList(ordered=False, items=[
                ListItem(content=["Item 1"]),
                ListItem(content=["Item 2 with ", FormattedText(text="emphasis", formats=[TextFormat.ITALIC])]),
            ]),
            DocumentList(ordered=True, items=[
                ListItem(content=["First"]),
                ListItem(content=["Second"]),
            ])
        ])

        # Convert to markdown and back
        markdown, _ = convert_docx_to_markdown(original_doc)
        converted_doc, _ = convert_markdown_to_docx(markdown)

        # Verify lists are preserved
        assert len(converted_doc.elements) == 2

        # Unordered list
        unordered_list = converted_doc.elements[0]
        assert isinstance(unordered_list, DocumentList)
        assert not unordered_list.ordered
        assert len(unordered_list.items) == 2

        # Ordered list
        ordered_list = converted_doc.elements[1]
        assert isinstance(ordered_list, DocumentList)
        assert ordered_list.ordered
        assert len(ordered_list.items) == 2

    def test_round_trip_with_table(self):
        """Test round-trip with tables."""
        original_doc = Document(elements=[
            Table(
                headers=[TableRow(cells=[
                    TableCell(content=["Name"]),
                    TableCell(content=["Age"])
                ])],
                rows=[
                    TableRow(cells=[
                        TableCell(content=["John"]),
                        TableCell(content=["25"])
                    ]),
                    TableRow(cells=[
                        TableCell(content=["Jane"]),
                        TableCell(content=["30"])
                    ])
                ]
            )
        ])

        # Convert to markdown and back
        markdown, _ = convert_docx_to_markdown(original_doc)
        converted_doc, _ = convert_markdown_to_docx(markdown)

        # Verify table is preserved
        assert len(converted_doc.elements) == 1
        table = converted_doc.elements[0]
        assert isinstance(table, Table)
        assert len(table.headers) == 1
        assert len(table.rows) == 2

    def test_round_trip_with_code_block(self):
        """Test round-trip with code blocks."""
        original_doc = Document(elements=[
            CodeBlock(language="python", code="print('hello')\nprint('world')"),
            CodeBlock(code="plain code")
        ])

        # Convert to markdown and back
        markdown, _ = convert_docx_to_markdown(original_doc)
        converted_doc, _ = convert_markdown_to_docx(markdown)

        # Verify code blocks are preserved
        assert len(converted_doc.elements) == 2

        code1 = converted_doc.elements[0]
        assert isinstance(code1, CodeBlock)
        assert code1.language == "python"
        assert code1.code == "print('hello')\nprint('world')"

        code2 = converted_doc.elements[1]
        assert isinstance(code2, CodeBlock)
        assert code2.language is None
        assert code2.code == "plain code"

    def test_round_trip_with_blockquote(self):
        """Test round-trip with blockquotes."""
        original_doc = Document(elements=[
            Blockquote(content=["This is a blockquote with ", FormattedText(text="emphasis", formats=[TextFormat.ITALIC])])
        ])

        # Convert to markdown and back
        markdown, _ = convert_docx_to_markdown(original_doc)
        converted_doc, _ = convert_markdown_to_docx(markdown)

        # Verify blockquote is preserved
        assert len(converted_doc.elements) == 1
        blockquote = converted_doc.elements[0]
        assert isinstance(blockquote, Blockquote)

    def test_formatting_preservation(self):
        """Test that text formatting is preserved in round-trip."""
        original_doc = Document(elements=[
            Paragraph(content=[
                "Plain text, ",
                FormattedText(text="bold text", formats=[TextFormat.BOLD]),
                ", ",
                FormattedText(text="italic text", formats=[TextFormat.ITALIC]),
                ", ",
                FormattedText(text="code text", formats=[TextFormat.CODE]),
                ", and ",
                FormattedText(text="link", link=Link(text="link", url="https://example.com")),
                "."
            ])
        ])

        # Convert to markdown and back
        markdown, _ = convert_docx_to_markdown(original_doc)
        converted_doc, _ = convert_markdown_to_docx(markdown)

        # Verify paragraph structure
        assert len(converted_doc.elements) == 1
        para = converted_doc.elements[0]
        assert isinstance(para, Paragraph)

        # Check that formatting is preserved (this is a simplified check)
        # In a real implementation, we'd need more sophisticated comparison
        assert len(para.content) > 1  # Should have multiple text elements

    def test_complex_document_round_trip(self):
        """Test round-trip with a complex document."""
        original_doc = Document(
            title="Complex Document",
            elements=[
                Heading(level=1, content=["Main Title"]),
                Paragraph(content=["Introduction paragraph."]),
                Heading(level=2, content=["Lists Section"]),
                DocumentList(ordered=False, items=[
                    ListItem(content=["Unordered item 1"]),
                    ListItem(content=["Unordered item 2"]),
                ]),
                DocumentList(ordered=True, items=[
                    ListItem(content=["Ordered item 1"]),
                    ListItem(content=["Ordered item 2"]),
                ]),
                Heading(level=2, content=["Code Section"]),
                CodeBlock(language="python", code="def hello():\n    print('Hello, World!')"),
                Heading(level=2, content=["Quote Section"]),
                Blockquote(content=["This is a famous quote."]),
                HorizontalRule(),
                Paragraph(content=["Conclusion."]),
            ]
        )

        # Convert to markdown and back
        markdown, warnings1 = convert_docx_to_markdown(original_doc)
        converted_doc, warnings2 = convert_markdown_to_docx(markdown)

        # Should have no warnings for supported elements
        assert warnings1 == []
        assert warnings2 == []

        # Verify basic structure (title not preserved in round-trip)
        assert converted_doc.title is None
        assert len(converted_doc.elements) >= 10  # Should preserve all elements

        # Check some key elements
        assert isinstance(converted_doc.elements[0], Heading)  # Title
        assert isinstance(converted_doc.elements[1], Paragraph)  # Intro
        assert isinstance(converted_doc.elements[2], Heading)  # Lists section
        # ... etc