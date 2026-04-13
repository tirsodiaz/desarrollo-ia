# Step 07 — CLI Adapter

## Goal
Implement the command-line interface. Parse arguments, call the application layer, and print results to stdout/stderr.

## Files
- `jano/src/jano/cli/adapter.py`
- `jano/src/jano/main.py`
- `jano/src/jano/__main__.py`

---

## `cli/adapter.py`

### Public interface

```python
def run_cli(args: list[str] | None = None) -> int:
    """
    Parse arguments and run conversion via the application layer.
    Returns exit code (0 = success, 1 = error).
    """
```

### CLI usage

```
jano <input_file> <output_file>
```

### Behaviour
- On success: print `Converted: <input> → <output>` to stdout
- On warning: print each warning to stderr as `[WARN] <element_type>: <description>`
- On error: print error message to stderr, return exit code 1
- `--help` / `-h`: print usage and exit 0

---

## `main.py`

```python
def main() -> None:
    """Entrypoint: dispatch to CLI or MCP based on sys.argv."""
    import sys
    if "--mcp" in sys.argv:
        from jano.mcp.adapter import run_mcp
        run_mcp()
    else:
        from jano.cli.adapter import run_cli
        sys.exit(run_cli())
```

---

## `__main__.py`

```python
from jano.main import main

if __name__ == "__main__":
    main()
```

---

## Acceptance criteria
- E2E test: `uv run python -m jano test-case/Que\ es\ un\ LLM.docx /tmp/out.md` exits 0 and produces a file
- E2E test: `uv run python -m jano test-case/Que\ es\ un\ LLM.md /tmp/out.docx` exits 0 and produces a file
- E2E test: missing arguments exits 1 with usage message on stderr
- `--mcp` flag does NOT enter CLI mode
