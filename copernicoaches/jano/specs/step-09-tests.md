# Step 09 — Tests

## Goal
Implement the test suite covering unit, integration, and end-to-end scenarios. Target coverage ≥ 90%.

## Test structure

```
tests/
  unit/
    test_docx_to_md.py     — domain: DOCX → MD conversion logic
    test_md_to_docx.py     — domain: MD → DOCX conversion logic
    test_models.py         — domain model construction and defaults
  integration/
    test_infrastructure.py — reader/writer round-trips
    test_application.py    — full convert_file() with real test-case files
  e2e/
    test_cli.py            — subprocess calls to `python -m jano`
    test_roundtrip.py      — repeated conversion stability test
```

---

## Key test cases

### Unit tests (no file I/O, use `python-docx` Document objects in-memory)

**`test_docx_to_md.py`**
- Heading 1 → `# Title`
- Heading 3 → `### Title`
- Bold run → `**text**`
- Italic run → `*text*`
- Hyperlink → `[label](url)`
- Bullet list item → `- item`
- Numbered list item → `1. item`
- Table (2×2) → valid GFM pipe table
- Image → warning emitted with `element_type="image"`

**`test_md_to_docx.py`**
- `# H1` → paragraph with `Heading 1` style
- `**bold**` → bold run
- GFM table → DOCX table with correct dimensions
- Fenced code block → `Code` style paragraph
- Raw HTML → warning with `element_type="raw_html"`

### Integration tests (use `dia4/test-case/` files)

**`test_application.py`**
- `convert_file("…/Que es un LLM.docx", tmp_path/"out.md")` — output file exists and is non-empty
- `convert_file("…/Que es un LLM.md", tmp_path/"out.docx")` — output file is a valid DOCX
- `ValueError` raised for `.txt` input

### E2E tests

**`test_cli.py`**
- `python -m jano input.docx output.md` → exit code 0, file created
- `python -m jano` (no args) → exit code 1, stderr contains usage
- `python -m jano bad.txt out.md` → exit code 1

**`test_roundtrip.py`**
- Convert `Que es un LLM.docx` → MD → DOCX → MD → DOCX (3 cycles)
- Assert each MD output contains headings, lists, and table content
- Assert no accumulated warnings about supported elements across cycles

---

## Running tests

```bash
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

## Acceptance criteria
- All tests pass
- Coverage ≥ 90% overall
- Roundtrip test passes for 3 cycles without degradation of supported elements
