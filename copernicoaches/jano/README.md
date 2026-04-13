# Jano

Bidirectional document converter between **Word (.docx)** and **Markdown (.md)**.

Jano preserves the logical structure and basic formatting of documents across conversions: headings, paragraphs, lists, tables, bold, italic, hyperlinks, blockquotes, and code blocks. Elements that cannot be fully converted are reported as warnings rather than silently dropped.

Jano can be used as a **CLI command** or as an **MCP tool** accessible from AI agents (e.g. Claude in VS Code).

![Jano](./images/jano2-small.png)

---

## Requirements

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) — used for all dependency management and command execution

---

## Installation

```bash
git clone <repo>
cd jano
uv sync
```

That's it. `uv sync` creates the virtual environment and installs all dependencies.

> **Note:** The `dev-mode-dirs = ["src"]` entry in `pyproject.toml` is required for the editable install to work correctly. Do not remove it.

---

## Usage

### CLI mode

Convert a Word document to Markdown:

```bash
uv run python -m jano input.docx output.md
```

Convert a Markdown file to Word:

```bash
uv run python -m jano input.md output.docx
```

On success, Jano prints the conversion summary to stdout:

```
Converted: input.docx → output.md
```

If any elements could not be fully preserved, warnings are printed to stderr:

```
[WARN] image: Image element cannot be converted to Markdown; replaced with [image].
```

On error (missing file, unsupported extension), Jano exits with code 1 and prints the error to stderr.

### MCP mode

Start Jano as a local MCP server (for use with AI agents):

```bash
uv run python -m jano --mcp
```

The server runs over stdio and exposes the `convert_document` tool with the following interface:

```
Tool:    convert_document
Inputs:  input_path  (string) — path to the source file (.docx or .md)
         output_path (string) — path for the output file (.md or .docx)
Output:  { "success": bool, "warnings": [...], "error": string | null }
```

To use Jano as an MCP tool from Claude in VS Code, add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "jano": {
      "command": "uv",
      "args": ["run", "python", "-m", "jano", "--mcp"],
      "cwd": "/absolute/path/to/jano"
    }
  }
}
```

---

## What is preserved

| Element              | DOCX → MD        | MD → DOCX         |
|----------------------|------------------|-------------------|
| Headings (H1–H6)     | `#` … `######`   | Heading 1–6 style |
| Paragraphs           | Plain text       | Normal style      |
| Bold                 | `**text**`       | Bold run          |
| Italic               | `*text*`         | Italic run        |
| Bold + italic        | `***text***`     | Bold + italic run |
| Hyperlinks           | `[text](url)`    | Word hyperlink    |
| Bullet lists         | `- item`         | List Bullet style |
| Numbered lists       | `1. item`        | List Number style |
| Nested lists         | Indent (2 spaces)| Increased level   |
| Tables               | GFM pipe table   | Table Grid style  |
| Blockquotes          | `> text`         | Indented paragraph|
| Code blocks          | Fenced ` ``` `   | Courier New font  |

## What is reported as a warning (not silently lost)

| Element    | Behaviour                                      |
|------------|------------------------------------------------|
| Images     | Replaced with `[image]` placeholder + warning  |
| Raw HTML   | Tags stripped, text kept + warning             |

---

## Project structure

```
jano/
  pyproject.toml          # single source of truth for deps, tools, config
  src/
    jano/
      __main__.py         # entry point: python -m jano
      main.py             # dispatch: CLI mode or MCP mode
      cli/
        adapter.py        # argument parsing, stdout/stderr output
      mcp/
        adapter.py        # FastMCP server, convert_document tool
      application/
        convert.py        # convert_file(): orchestrates all layers
      domain/
        models.py         # ConversionResult, ConversionWarning, ConversionDirection
        docx_to_md.py     # DOCX → Markdown conversion logic (pure, no I/O)
        md_to_docx.py     # Markdown → DOCX conversion logic (pure, no I/O)
      infrastructure/
        reader.py         # read_docx(), read_md() — file input
        writer.py         # write_docx(), write_md() — file output
  tests/
    unit/                 # domain logic, CLI adapter, MCP adapter, main dispatch
    integration/          # infrastructure round-trips, application layer
    e2e/                  # subprocess CLI calls, multi-cycle roundtrip stability
  test-case/
    Que es un LLM.docx    # reference document for validation
    Que es un LLM.md      # equivalent Markdown for validation
  specs/                  # implementation step specifications (10 steps)
```

### Architectural principles

Jano follows a strict layered architecture with no cross-layer coupling:

- **CLI and MCP adapters** only handle I/O and protocol — no conversion logic.
- **Application layer** (`convert_file`) is the single entry point used by both adapters.
- **Domain layer** is pure Python — no file handles, no paths, no external I/O.
- **Infrastructure layer** is the only place that touches the filesystem.

This means the same conversion logic runs identically in CLI and MCP mode.

---

## Development

### Run tests

```bash
uv run pytest
```

With coverage report:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

### Lint and format

```bash
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

### Full validation pipeline

```bash
uv sync && \
uv run ruff check src/ tests/ && \
uv run ruff format --check src/ tests/ && \
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

Current status: **64 tests pass, 91% coverage**.

---

## Test case

The `test-case/` directory contains two equivalent documents (`Que es un LLM.docx` and `Que es un LLM.md`) covering all supported elements: headings, paragraphs, bold, italic, lists, tables, blockquotes, code blocks, and hyperlinks.

These are used both for manual inspection and for the automated roundtrip stability test, which converts the same document through 3 full cycles (DOCX → MD → DOCX → MD → DOCX → MD and the reverse) and verifies that no supported content is lost across cycles.

---

## Dependencies

| Package          | Purpose                              |
|------------------|--------------------------------------|
| `python-docx`    | Read and write Word documents        |
| `markdown-it-py` | Parse Markdown into a token tree     |
| `fastmcp`        | MCP server implementation            |
| `pytest`         | Test runner (dev)                    |
| `pytest-cov`     | Coverage reporting (dev)             |
| `ruff`           | Linting and formatting (dev)         |
