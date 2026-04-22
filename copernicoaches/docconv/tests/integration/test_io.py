"""
Integration tests for I/O operations.

Tests round-trip conversion and file handling.
"""

import os
import tempfile
import pytest
from pathlib import Path

from docconv.infrastructure import read_docx, read_markdown, write_docx, write_markdown
from docconv.domain.models import Document, Paragraph, Heading, FormattedText, TextFormat


class TestDocxIO:
    """Test DOCX file I/O operations."""

    def test_round_trip_simple_document(self):
        """Test round-trip conversion: create document -> write DOCX -> read DOCX."""
        # Create a simple document
        doc = Document(elements=[
            Heading(level=1, content=["Test Document"]),
            Paragraph(content=["This is a test paragraph."]),
        ])

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Write to DOCX
            warnings_write = write_docx(doc, tmp_path)
            assert len(warnings_write) == 0, f"Write warnings: {warnings_write}"

            # Read back from DOCX
            read_doc, warnings_read = read_docx(tmp_path)
            assert read_doc is not None, f"Read failed with warnings: {warnings_read}"
            assert len(warnings_read) == 0, f"Read warnings: {warnings_read}"

            # Verify structure (basic check)
            assert len(read_doc.elements) >= 1  # At least the heading

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_read_nonexistent_file(self):
        """Test reading a non-existent DOCX file."""
        doc, warnings = read_docx("/nonexistent/file.docx")
        assert doc is None
        assert len(warnings) == 1
        assert "does not exist" in warnings[0].description

    def test_write_to_invalid_path(self):
        """Test writing to an invalid path."""
        doc = Document(elements=[Paragraph(content=["test"])])
        # Use a path that will definitely fail (trying to write to a system directory)
        invalid_path = "C:\\Windows\\System32\\test.docx"
        warnings = write_docx(doc, invalid_path)
        assert len(warnings) >= 1
        assert "Failed to write" in warnings[0].description


class TestMarkdownIO:
    """Test Markdown file I/O operations."""

    def test_round_trip_simple_document(self):
        """Test round-trip conversion: create document -> write MD -> read MD."""
        # Create a simple document
        doc = Document(elements=[
            Heading(level=1, content=["Test Document"]),
            Paragraph(content=["This is a test paragraph with ", FormattedText(text="bold", formats=[TextFormat.BOLD]), " text."]),
        ])

        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Write to Markdown
            warnings_write = write_markdown(doc, tmp_path)
            assert len(warnings_write) == 0, f"Write warnings: {warnings_write}"

            # Read back from Markdown
            read_doc, warnings_read = read_markdown(tmp_path)
            assert read_doc is not None, f"Read failed with warnings: {warnings_read}"
            assert len(warnings_read) == 0, f"Read warnings: {warnings_read}"

            # Verify structure
            assert len(read_doc.elements) == 2
            assert isinstance(read_doc.elements[0], Heading)
            assert read_doc.elements[0].level == 1
            assert isinstance(read_doc.elements[1], Paragraph)

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_read_nonexistent_file(self):
        """Test reading a non-existent Markdown file."""
        doc, warnings = read_markdown("/nonexistent/file.md")
        assert doc is None
        assert len(warnings) == 1
        assert "does not exist" in warnings[0].description

    def test_write_to_invalid_path(self):
        """Test writing to an invalid path."""
        doc = Document(elements=[Paragraph(content=["test"])])
        # Use a path that will definitely fail (trying to write to a system directory)
        invalid_path = "C:\\Windows\\System32\\test.md"
        warnings = write_markdown(doc, invalid_path)
        assert len(warnings) >= 1
        assert "Failed to write" in warnings[0].description

    def test_read_write_complex_markdown(self):
        """Test reading and writing complex Markdown content."""
        markdown_content = """# Main Title

This is a paragraph with **bold** and *italic* text.

## Section

- Bullet 1
- Bullet 2

```python
print("hello")
```

> This is a blockquote
"""

        # Write to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp:
            tmp.write(markdown_content)
            tmp_path = tmp.name

        try:
            # Read the file
            doc, warnings_read = read_markdown(tmp_path)
            assert doc is not None, f"Read failed: {warnings_read}"
            assert len(warnings_read) == 0, f"Read warnings: {warnings_read}"

            # Write back to another file
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp2:
                tmp_path2 = tmp2.name

            warnings_write = write_markdown(doc, tmp_path2)
            assert len(warnings_write) == 0, f"Write warnings: {warnings_write}"

            # Read back the written file
            doc2, warnings_read2 = read_markdown(tmp_path2)
            assert doc2 is not None, f"Re-read failed: {warnings_read2}"
            assert len(warnings_read2) == 0, f"Re-read warnings: {warnings_read2}"

            # Basic structure check
            assert len(doc.elements) == len(doc2.elements)

        finally:
            for path in [tmp_path, tmp_path2]:
                if os.path.exists(path):
                    os.unlink(path)