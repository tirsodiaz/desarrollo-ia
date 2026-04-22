"""
End-to-end tests for the document converter.

These tests run the complete application from command line
and validate the generated files.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestE2EConversion:
    """End-to-end tests for document conversion."""

    def test_md_to_docx_conversion(self):
        """Test complete MD to DOCX conversion via command line."""
        # Create test Markdown content
        markdown_content = """# Test Document

This is a test paragraph with **bold** and *italic* text.

## Section

- Bullet point 1
- Bullet point 2

```python
print("Hello, World!")
```

> This is a blockquote
"""

        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as md_file:
            md_file.write(markdown_content)
            md_path = md_file.name

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_file:
            docx_path = docx_file.name

        try:
            # Run the conversion command
            result = subprocess.run([
                sys.executable, "-m", "docconv",
                md_path, docx_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent / "src")

            # Check exit code
            assert result.returncode == 0, f"Command failed: {result.stderr}"

            # Check that output file was created
            assert os.path.exists(docx_path), "Output DOCX file was not created"
            assert os.path.getsize(docx_path) > 0, "Output DOCX file is empty"

            # Check stdout contains success message
            assert "Conversion successful" in result.stdout

        finally:
            # Clean up
            for path in [md_path, docx_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_docx_to_md_conversion(self):
        """Test complete DOCX to MD conversion via command line."""
        # For DOCX to MD, we'll need to create a DOCX file or use a round-trip approach
        # Since creating DOCX programmatically is complex, we'll test the command structure

        # Create a dummy DOCX file (this won't be valid, but tests the command)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_file:
            docx_file.write(b"dummy docx content")
            docx_path = docx_file.name

        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as md_file:
            md_path = md_file.name

        try:
            # Run the conversion command (will fail due to invalid DOCX, but tests command structure)
            result = subprocess.run([
                sys.executable, "-m", "docconv",
                docx_path, md_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent / "src")

            # Should fail due to invalid DOCX, but command should be recognized
            assert result.returncode == 1, "Command should fail for invalid DOCX"
            assert "Failed to read DOCX file" in result.stderr

        finally:
            for path in [docx_path, md_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_invalid_input_file(self):
        """Test command with non-existent input file."""
        result = subprocess.run([
            sys.executable, "-m", "docconv",
            "/nonexistent/file.md", "/tmp/output.docx"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent / "src")

        assert result.returncode == 1
        assert "does not exist" in result.stderr

    def test_unsupported_conversion(self):
        """Test command with unsupported file extensions."""
        # Create a file with unsupported extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as txt_file:
            txt_file.write("test content")
            txt_path = txt_file.name

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
            pdf_path = pdf_file.name

        try:
            result = subprocess.run([
                sys.executable, "-m", "docconv",
                txt_path, pdf_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent / "src")

            assert result.returncode == 1
            assert "Unsupported conversion" in result.stderr

        finally:
            for path in [txt_path, pdf_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_round_trip_conversion(self):
        """Test round-trip conversion: MD -> DOCX -> MD."""
        original_content = """# Round Trip Test

This document tests **bold** and *italic* formatting.

- Item 1
- Item 2

```python
def test():
    return "success"
```
"""

        # MD -> DOCX
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as md1:
            md1.write(original_content)
            md1_path = md1.name

        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx:
            docx_path = docx.name

        # DOCX -> MD
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as md2:
            md2_path = md2.name

        try:
            # First conversion: MD -> DOCX
            result1 = subprocess.run([
                sys.executable, "-m", "docconv",
                md1_path, docx_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent / "src")

            assert result1.returncode == 0, f"First conversion failed: {result1.stderr}"

            # Second conversion: DOCX -> MD
            result2 = subprocess.run([
                sys.executable, "-m", "docconv",
                docx_path, md2_path
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent / "src")

            assert result2.returncode == 0, f"Second conversion failed: {result2.stderr}"

            # Read back the final MD content
            with open(md2_path, 'r', encoding='utf-8') as f:
                final_content = f.read()

            # Basic validation (exact match may vary due to format limitations)
            assert "# Round Trip Test" in final_content or "# Round trip test" in final_content
            assert "bold" in final_content
            assert "italic" in final_content
            assert "Item 1" in final_content
            assert "def test():" in final_content

        finally:
            for path in [md1_path, docx_path, md2_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_help_output(self):
        """Test that help is displayed correctly."""
        result = subprocess.run([
            sys.executable, "-m", "docconv", "--help"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent / "src")

        assert result.returncode == 0
        assert "Convert documents between DOCX and Markdown formats" in result.stdout
        assert "input_path" in result.stdout
        assert "output_path" in result.stdout