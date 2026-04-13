# Madriguera

> Un sistema de procesamiento automático basado en archivos

![Madriguera](./images/madriguera-small.png)

## Overview

Madriguera is a long-running local console application that watches an inbox directory for JSON files, processes each file through a staged pipeline, persists traceability data in SQLite, writes successful results to an outbox, writes failures to an errors directory, and archives the original processed input.

The application is intentionally file-driven. There is no web API and no external network integration in this implementation. All external dependencies are simulated with JSON files stored under a configuration directory.

## What The App Does

For each incoming case file, Madriguera executes this flow:

1. Detect a new `.json` file in the inbox.
2. Move it into the processing directory.
3. Read and parse the JSON into a typed `CaseInput`.
4. Validate the payload.
5. Read simulated external data from config files:
   - account balances
   - non-working calendar days
   - business rules
6. Apply the business decision rules.
7. Persist processing state in SQLite.
8. Write either:
   - a success JSON file to the outbox
   - or an error JSON file to the errors directory
9. Move the processed source file into the archive directory.

## Main Components

- `src/app/cli`: CLI entry point and runtime bootstrapping
- `src/app/config`: typed application settings
- `src/app/domain`: Pydantic models and pure business rules
- `src/app/application`: service layer, ports, and business processor
- `src/app/pipeline`: pipeline envelope, engine, and stages
- `src/app/infrastructure/filesystem`: config readers and output writers
- `src/app/infrastructure/persistence`: SQLAlchemy models, repository, unit of work, Alembic
- `src/app/infrastructure/watcher`: file watcher implementation

## Runtime Directories

By default, Madriguera uses these paths:

- `data/inbox`
- `data/processing`
- `data/outbox`
- `data/errors`
- `data/archive`
- `data/config`
- `madriguera.db`

The directories are created automatically on startup if they do not already exist.

## Configuration

Settings are loaded from environment variables and optionally from a `.env` file.

Supported settings:

- `INBOX_DIR`
- `PROCESSING_DIR`
- `OUTBOX_DIR`
- `ERRORS_DIR`
- `ARCHIVE_DIR`
- `CONFIG_DIR`
- `DATABASE_URL`
- `LOG_LEVEL`
- `ACTIVE_PROCESSOR`
- `FILE_STABILISATION_SECONDS`

The default script entry point is:

```bash
madriguera run
```

## Install

Use `uv`, not `pip`.

### Requirements

- Python 3.13+
- `uv`

### Sync The Environment

```bash
uv sync
```

If you also want the test dependencies explicitly available in the environment:

```bash
uv sync --dev
```

## Run The App

Start Madriguera with the default local runtime:

```bash
uv run madriguera run
```

You should see a startup log similar to:

```json
{"event": "Madriguera started. Watching: data/inbox", "level": "info", ...}
```

Stop it with `Ctrl+C`.

## Run The Tests

```bash
uv run pytest tests/unit
```

## Seed Data Already In The Repo

Default simulated config is under `data/config/`:

- `balances.json`
- `calendar.json`
- `rules.json`

Sample inbox cases are under `data/inbox/`:

- `case_positive.json`
- `case_zero.json`
- `case_neg_cli.json`
- `case_neg_bank.json`
- `case_wait.json`
- `case_cancel.json`

These files are useful as reference data, but for a clean manual run you should prefer the isolated test case below.

## Manual Test Case

An isolated manual positive-balance test case is included under:

```text
test-case/manual-positive/
```

It contains:

- `config/`: the simulated external data for the run
- `input/`: the file you will drop into the inbox
- `expected/`: the expected outbox result

### Manual Test Data In

Input case file:

`test-case/manual-positive/input/case_manual_positive.json`

```json
{
  "caseId": "CASE_MANUAL_001",
  "source": "CLI",
  "contracts": [
    {
      "contractId": "ACC_001"
    }
  ],
  "accountClosure": {
    "dateToCheckBalance": null,
    "entity": "0014"
  }
}
```

Why this produces a positive result:

- `contracts[0].contractId` is `ACC_001`
- `test-case/manual-positive/config/balances.json` maps `ACC_001` to `120.5`
- a positive balance produces `positiveBalance`

### Start The App Against The Manual Test Runtime

Run the app with isolated runtime paths so you do not reuse the default database or inbox state:

```bash
INBOX_DIR=./test-case/manual-positive/runtime/inbox \
PROCESSING_DIR=./test-case/manual-positive/runtime/processing \
OUTBOX_DIR=./test-case/manual-positive/runtime/outbox \
ERRORS_DIR=./test-case/manual-positive/runtime/errors \
ARCHIVE_DIR=./test-case/manual-positive/runtime/archive \
CONFIG_DIR=./test-case/manual-positive/config \
DATABASE_URL=sqlite:///./test-case/manual-positive/runtime/manual-test.db \
uv run madriguera run
```

Madriguera will create the `runtime/` directories automatically on startup.

### Add The Manual Test Data

In a second terminal, copy the input file into the watched inbox:

```bash
cp ./test-case/manual-positive/input/case_manual_positive.json \
   ./test-case/manual-positive/runtime/inbox/
```

### Expected Result

After the file is processed, the expected behavior is:

1. `test-case/manual-positive/runtime/outbox/CASE_MANUAL_001.json` exists
2. `test-case/manual-positive/runtime/errors/` stays empty
3. `test-case/manual-positive/runtime/archive/case_manual_positive.json` exists
4. `test-case/manual-positive/runtime/manual-test.db` contains a `SUCCESS` record for the processed file

Expected outbox payload:

`test-case/manual-positive/expected/CASE_MANUAL_001.json`

```json
{
  "caseId": "CASE_MANUAL_001",
  "action": "positiveBalance",
  "dateTime": null
}
```

You can compare the generated file with the expected fixture:

```bash
diff \
  ./test-case/manual-positive/expected/CASE_MANUAL_001.json \
  ./test-case/manual-positive/runtime/outbox/CASE_MANUAL_001.json
```

No output from `diff` means the generated file matches the expected result.

## Notes For Repeated Manual Runs

- Idempotency is tracked by source file path in the database.
- If you reuse the same inbox path and same SQLite file, re-dropping the same file path will be skipped as already processed.
- For a fresh rerun, remove `test-case/manual-positive/runtime/` or point `DATABASE_URL` to a new SQLite file before restarting the app.

## Output And Error Formats

Successful output files look like:

```json
{
  "caseId": "CASE_001",
  "action": "positiveBalance",
  "dateTime": null
}
```

Wait results include a timestamp:

```json
{
  "caseId": "CASE_003",
  "action": "wait",
  "dateTime": "2026-03-25T00:01:00"
}
```

Error files look like:

```json
{
  "caseId": "CASE_001",
  "taskName": "Check Account Balance",
  "dateTime": "2026-03-20T10:00:00",
  "errors": [
    {
      "code": "ERR_BALANCE_NOT_FOUND",
      "message": "No balance configured for account: ACC_001"
    }
  ]
}
```
