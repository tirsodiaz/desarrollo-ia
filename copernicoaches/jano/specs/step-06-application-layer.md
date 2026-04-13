# Step 06 — Application Layer

## Goal
Orchestrate the use cases by combining infrastructure (I/O) and domain (conversion logic). This is the single entry point for all interfaces (CLI and MCP).

## File
`jano/src/jano/application/convert.py`

## Dependencies
- `jano.domain.docx_to_md`
- `jano.domain.md_to_docx`
- `jano.domain.models`
- `jano.infrastructure.reader`
- `jano.infrastructure.writer`

## Public interface

```python
def convert_file(input_path: str, output_path: str) -> ConversionResult:
    """
    Detect conversion direction from file extensions, run conversion,
    write output, and return the result (including any warnings).

    Supported conversions:
      .docx → .md
      .md   → .docx
    """
```

## Direction detection logic

| Input extension | Output extension | Action                  |
|-----------------|------------------|-------------------------|
| `.docx`         | `.md`            | `convert_docx_to_md`    |
| `.md`           | `.docx`          | `convert_md_to_docx`    |
| anything else   | —                | raise `ValueError`      |

## Rules
- The application layer MUST NOT parse CLI arguments or handle MCP protocol
- The application layer MUST NOT contain file format parsing logic
- Warnings from the domain layer MUST be passed through to the caller unchanged

## Acceptance criteria
- Integration test: `convert_file("Que es un LLM.docx", "out.md")` produces a non-empty Markdown file
- Integration test: `convert_file("Que es un LLM.md", "out.docx")` produces a valid DOCX file
- `ValueError` raised for unsupported extension combination
- Warnings are returned (not swallowed)
