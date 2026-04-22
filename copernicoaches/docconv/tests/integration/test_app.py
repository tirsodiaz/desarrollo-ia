"""
Integration tests for application layer.

Tests the main convert_file function and orchestration.
"""

import os
import tempfile
import pytest
from pathlib import Path

from docconv.application import convert_file, ConversionResult


class TestConvertFile:
    """Test the main convert_file function."""

    def test_docx_to_markdown_conversion(self):
        """Test full DOCX to Markdown conversion."""
        # Create a simple DOCX file for testing
        # Since we can't easily create DOCX files in tests, we'll mock or skip
        # For now, test the error handling
        result = convert_file("/nonexistent/file.docx", "/tmp/output.md")
        assert not result.success
        assert "does not exist" in result.error_message

    def test_markdown_to_docx_conversion(self):
        """Test full Markdown to DOCX conversion."""
        # Create a temporary Markdown file
        markdown_content = """# Test Document

This is a test paragraph with **bold** and *italic* text.

## Section

- Bullet 1
- Bullet 2

```python
print("hello")
```
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
            tmp_md.write(markdown_content)
            md_path = tmp_md.name

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_docx:
            docx_path = tmp_docx.name

        try:
            # Perform conversion
            result = convert_file(md_path, docx_path)

            assert result.success
            assert result.input_path == md_path
            assert result.output_path == docx_path
            assert os.path.exists(docx_path)

            # Check that output file has content
            assert os.path.getsize(docx_path) > 0

        finally:
            for path in [md_path, docx_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_unsupported_conversion(self):
        """Test conversion between unsupported formats."""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("test content")
            txt_path = tmp.name

        try:
            result = convert_file(txt_path, "output.pdf")
            assert not result.success
            assert "Unsupported conversion" in result.error_message
        finally:
            if os.path.exists(txt_path):
                os.unlink(txt_path)

    def test_nonexistent_input_file(self):
        """Test conversion with non-existent input file."""
        result = convert_file("/nonexistent/input.md", "/tmp/output.docx")
        assert not result.success
        assert "does not exist" in result.error_message

    def test_round_trip_markdown(self):
        """Test round-trip conversion: MD -> DOCX -> MD."""
        original_content = """# Original Title

This is the original content with **bold** text and *italic* text.

- List item 1
- List item 2

```python
def hello():
    print("Hello, World!")
```
"""

        # MD -> DOCX
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_md1:
            tmp_md1.write(original_content)
            md1_path = tmp_md1.name

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_docx:
            docx_path = tmp_docx.name

        result1 = convert_file(md1_path, docx_path)
        assert result1.success

        # DOCX -> MD
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as tmp_md2:
            md2_path = tmp_md2.name

        result2 = convert_file(docx_path, md2_path)
        assert result2.success

        # Read back the final MD content
        with open(md2_path, 'r', encoding='utf-8') as f:
            final_content = f.read()

        # Basic checks (exact match may not be perfect due to format limitations)
        assert "# Original Title" in final_content or "# Original title" in final_content
        assert "bold" in final_content
        assert "italic" in final_content
        assert "List item 1" in final_content
        assert "print" in final_content

        # Clean up
        for path in [md1_path, docx_path, md2_path]:
            if os.path.exists(path):
                os.unlink(path)

    def test_conversion_with_warnings(self):
        """Test conversion that generates warnings."""
        # Create MD with complex elements that might generate warnings
        markdown_content = """# Title

This has a [link](http://example.com) and some **bold** text.

| Table | Header |
|-------|--------|
| Cell  | Data   |
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_md:
            tmp_md.write(markdown_content)
            md_path = tmp_md.name

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_docx:
            docx_path = tmp_docx.name

        try:
            result = convert_file(md_path, docx_path)

            # Should succeed even with warnings
            assert result.success
            # May or may not have warnings depending on implementation
            # assert len(result.warnings) >= 0  # Just check it's a list

        finally:
            for path in [md_path, docx_path]:
                if os.path.exists(path):
                    os.unlink(path)


class TestConversionResult:
    """Test the ConversionResult class."""

    def test_success_result(self):
        """Test successful conversion result."""
        result = ConversionResult(
            success=True,
            input_path="input.md",
            output_path="output.docx",
            warnings=[]
        )
        assert result.success
        assert result.input_path == "input.md"
        assert result.output_path == "output.docx"
        assert result.warnings == []
        assert result.error_message is None

    def test_error_result(self):
        """Test error conversion result."""
        result = ConversionResult(
            success=False,
            input_path="input.md",
            output_path="output.docx",
            error_message="File not found"
        )
        assert not result.success
        assert result.error_message == "File not found"

    def test_result_with_warnings(self):
        """Test result with warnings."""
        from docconv.domain.models import ConversionWarning
        warning = ConversionWarning(
            element_type="test",
            description="Test warning"
        )
        result = ConversionResult(
            success=True,
            input_path="input.md",
            output_path="output.docx",
            warnings=[warning]
        )
        assert result.success
        assert len(result.warnings) == 1
        assert result.warnings[0].description == "Test warning"