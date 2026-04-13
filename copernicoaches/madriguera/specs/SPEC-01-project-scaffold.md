# SPEC-01 — Project Scaffold, Configuration & CLI Skeleton

## Goal

Establish the full project directory structure, configuration loading, and a working CLI entry point that can be started and stopped cleanly. No business logic in this spec.

---

## Scope

- Project layout matching the architecture layers
- Typed configuration loaded from environment and/or `.env` file
- CLI with a `run` command that starts a placeholder loop
- Structured logging initialised at startup
- All runtime directories created automatically on startup if they do not exist

---

## Deliverables

### 1. Project structure

Create the following directory tree inside `madriguera/src/app/`:

```text
src/
  app/
    __init__.py
    main.py                  ← entry point called by CLI
    cli/
      __init__.py
      commands.py            ← Typer app with `run` command
    config/
      __init__.py
      settings.py            ← AppSettings via pydantic-settings
    pipeline/                ← empty package, populated in SPEC-05
    domain/                  ← empty package, populated in SPEC-02
    application/             ← empty package, populated in SPEC-07
    infrastructure/
      __init__.py
      watcher/               ← empty package, populated in SPEC-06
      filesystem/            ← empty package, populated in SPEC-06 / SPEC-08
      persistence/           ← empty package, populated in SPEC-04
tests/
  __init__.py
  unit/
    __init__.py
  integration/
    __init__.py
```

All leaf files (`__init__.py`) may be empty at this stage.

### 2. Configuration — `src/app/config/settings.py`

Use `pydantic-settings`. Define `AppSettings` with the following fields and defaults:

| Field | Type | Default | Description |
|---|---|---|---|
| `inbox_dir` | `Path` | `./data/inbox` | Input directory |
| `processing_dir` | `Path` | `./data/processing` | In-progress directory |
| `outbox_dir` | `Path` | `./data/outbox` | Successful results |
| `errors_dir` | `Path` | `./data/errors` | Error results |
| `archive_dir` | `Path` | `./data/archive` | Processed source files |
| `config_dir` | `Path` | `./data/config` | Simulation config files |
| `database_url` | `str` | `sqlite:///./madriguera.db` | SQLAlchemy DB URL |
| `log_level` | `str` | `INFO` | Python logging level |
| `active_processor` | `str` | `check_account_balance` | Processor to use |
| `file_stabilisation_seconds` | `float` | `0.5` | Wait before reading a new file |

Load from a `.env` file using `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")`.

All directory fields must use `Path` (not raw strings).

### 3. CLI — `src/app/cli/commands.py`

Use `Typer`. Expose one command: `run`.

`run` must:
1. Load `AppSettings`
2. Initialise structured logging at the configured level
3. Create all configured directories if they do not already exist (`mkdir -p` equivalent)
4. Log a startup message: `"Madriguera started. Watching: <inbox_dir>"`
5. Enter a blocking loop (placeholder: `while True: time.sleep(1)`)
6. Handle `KeyboardInterrupt` cleanly with a shutdown log message: `"Madriguera stopped."`

### 4. Entry point — `src/app/main.py`

```python
from app.cli.commands import app

if __name__ == "__main__":
    app()
```

### 5. `pyproject.toml` adjustments

Ensure the following dependencies are declared:
- `typer[all]`
- `pydantic>=2.0`
- `pydantic-settings`
- `sqlalchemy>=2.0`
- `alembic`
- `watchdog`
- `structlog` (or rely on stdlib `logging` — either is acceptable)
- `pytest` (dev dependency)

Declare a script entry point so the application can be started with:
```
madriguera run
```

---

## Validations

All of the following must pass before this spec is considered complete.

### V-01 — Directories are created on startup

Run `madriguera run` pointing to a fresh empty directory. Verify that `inbox`, `processing`, `outbox`, `errors`, `archive`, and `config` subdirectories are created automatically.

**How to verify:** After startup, inspect the filesystem. All six directories must exist.

### V-02 — Configuration can be overridden via environment variable

Set `INBOX_DIR=/tmp/test_inbox` in the shell (or `.env` file). Start the application. Verify the log message says `Watching: /tmp/test_inbox`.

**How to verify:** Read the startup log output.

### V-03 — Clean shutdown on Ctrl+C

Start the application. Send `KeyboardInterrupt` (Ctrl+C). Verify the shutdown message is logged and the process exits with code 0.

**How to verify:** Check process exit code and log output.

### V-04 — Settings unit test

Write `tests/unit/test_settings.py`. Test that:
- `AppSettings()` instantiates with defaults
- A custom `inbox_dir` value is accepted
- `log_level` defaults to `"INFO"`

```python
def test_default_settings():
    s = AppSettings()
    assert s.log_level == "INFO"
    assert s.active_processor == "check_account_balance"
```

### V-05 — Project installs cleanly

Run `uv install` (or `pip install -e .`). Verify `madriguera run --help` prints a usage message without errors.

---

## Decisions made

- `pydantic-settings` is used instead of raw `os.environ` to get validated, typed config.
- Directories are created at startup, not at package import time, to avoid side effects during tests.
- `Typer` is used for the CLI; it wraps `Click` and works well with type hints.
- The placeholder loop in `run` is intentionally simple; the real watcher will be added in SPEC-06.

---

## References

- Architecture guide: `madriguera/architecture-definition.md` — sections "CLI / runtime layer", "Configuration model", "Suggested project structure"
- Recommended stack: `madriguera/architecture-definition.md` — section "Recommended stack"
