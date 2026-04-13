# Step 10 — Quality Checks and Final Validation

## Goal
Enforce code quality with Ruff and run the full validation pipeline.

## Commands

```bash
cd jano

# Format
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Tests with coverage
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

## Ruff configuration (in `pyproject.toml`)

```toml
[tool.ruff]
line-length = 88
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "I"]   # pycodestyle errors, pyflakes, isort
```

## Full validation pipeline (single command)

```bash
uv sync && \
uv run ruff check src/ tests/ && \
uv run ruff format --check src/ tests/ && \
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

## Manual validation checklist

Run both conversions with the provided test case and inspect output:

```bash
# DOCX → MD
uv run python -m jano ../dia4/test-case/"Que es un LLM.docx" /tmp/out.md
cat /tmp/out.md

# MD → DOCX
uv run python -m jano ../dia4/test-case/"Que es un LLM.md" /tmp/out.docx
```

Open `/tmp/out.docx` in LibreOffice or Word and verify:
- [ ] Headings render at correct levels
- [ ] Bold and italic text is preserved
- [ ] Bullet and numbered lists are intact
- [ ] Table structure is present
- [ ] Blockquote and code blocks are distinguishable
- [ ] Links are clickable

## Acceptance criteria
- `ruff check` exits 0
- `ruff format --check` exits 0
- `pytest --cov-fail-under=90` exits 0
- Manual inspection passes all checklist items
