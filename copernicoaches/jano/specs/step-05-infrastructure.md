# Step 05 — Infrastructure Layer

## Goal
Implement file I/O: reading input files and writing output files. No conversion logic here.

## Files
- `jano/src/jano/infrastructure/reader.py`
- `jano/src/jano/infrastructure/writer.py`

---

## `reader.py`

### Public interface

```python
def read_docx(path: str) -> Document:
    """Load and return a python-docx Document from the given file path."""

def read_md(path: str) -> str:
    """Read and return the text content of a Markdown file."""
```

### Rules
- Raise `FileNotFoundError` if the path does not exist
- Raise `ValueError` if the extension does not match the expected format

---

## `writer.py`

### Public interface

```python
def write_md(content: str, path: str) -> None:
    """Write Markdown string to the given file path."""

def write_docx(content: bytes, path: str) -> None:
    """Write DOCX bytes to the given file path."""
```

### Rules
- Create parent directories if they do not exist
- Overwrite without prompting (CLI layer is responsible for user confirmation if needed)

---

## Acceptance criteria
- Integration test: write a temp MD file, read it back, content matches
- Integration test: write a temp DOCX (bytes from domain layer), read it back with `python-docx`, document loads successfully
- `FileNotFoundError` raised for missing input file
- `ValueError` raised for wrong file extension
