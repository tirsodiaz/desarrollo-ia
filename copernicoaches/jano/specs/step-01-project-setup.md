# Step 01 — Project Setup

## Goal
Initialize the Python project for Jano using `uv` with the mandatory toolchain and directory structure.

## Target location
`jano/src/`

## Actions

### 1. Initialize uv project
```bash
cd jano
uv init --package jano
```

This creates `pyproject.toml` and a basic package skeleton.

### 2. Set project structure
Ensure the following layout exists under `jano/`:

```
jano/
  pyproject.toml
  src/
    jano/
      __init__.py
      __main__.py
      main.py
      cli/
        __init__.py
        adapter.py
      mcp/
        __init__.py
        adapter.py
      application/
        __init__.py
        convert.py
      domain/
        __init__.py
        docx_to_md.py
        md_to_docx.py
        models.py
      infrastructure/
        __init__.py
        reader.py
        writer.py
  tests/
    __init__.py
    unit/
      __init__.py
    integration/
      __init__.py
    e2e/
      __init__.py
  test-case/
    (copy from dia4/test-case)
```

### 3. Configure `pyproject.toml`

```toml
[project]
name = "jano"
version = "0.1.0"
description = "Bidirectional Word ↔ Markdown converter"
requires-python = ">=3.11"
dependencies = [
    "python-docx>=1.1",
    "markdown-it-py>=3.0",
    "fastmcp>=0.1",
]

[project.scripts]
jano = "jano.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/jano"]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
]

[tool.ruff]
line-length = 88
src = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 4. Sync dependencies
```bash
uv sync
```

## Acceptance criteria
- `uv sync` completes without errors
- `uv run python -m jano --help` runs (even if it just prints usage)
- Directory structure matches the spec above
