# SPEC-08 — Outbound Adapter: Output Writers & Archive

## Goal

Implement `EmitStage` and `ArchiveStage`. `EmitStage` writes the final result to `outbox/` on success or to `errors/` on failure. `ArchiveStage` moves the processed source file from `processing/` to `archive/`. After this spec, the full end-to-end pipeline is operational.

---

## Scope

- `OutputWriter`: serialises a `DomainResult` to an `OutputPayload` JSON file in `outbox/`
- `ErrorWriter`: serialises a `PipelineEnvelope` failure to an `ErrorPayload` JSON file in `errors/`
- `EmitStage`: calls the appropriate writer based on the envelope status
- `ArchiveStage`: moves the source file from `processing/` to `archive/`
- Final `FileProcessingService` update to handle error-path envelope
- End-to-end integration tests covering all six scenario files

---

## Deliverables

### 1. Output writer — `src/app/infrastructure/filesystem/writers.py`

```python
from app.domain.models import DomainResult, OutputPayload, ErrorPayload, ErrorEntry
from pathlib import Path
import json
from datetime import datetime

class OutputWriter:
    def __init__(self, outbox_dir: Path):
        self._outbox_dir = outbox_dir

    def write(self, result: DomainResult) -> Path:
        payload = OutputPayload(
            caseId=result.case_id,
            action=result.action,
            dateTime=result.date_time.isoformat() if result.date_time else None,
        )
        out_file = self._outbox_dir / f"{result.case_id}.json"
        out_file.write_text(
            payload.model_dump_json(indent=2),
            encoding="utf-8"
        )
        return out_file
```

Output filename: `<caseId>.json` in the `outbox/` directory. If a file with that name already exists, overwrite it.

### 2. Error writer — `src/app/infrastructure/filesystem/writers.py`

```python
class ErrorWriter:
    def __init__(self, errors_dir: Path):
        self._errors_dir = errors_dir

    def write(self, case_id: str, error_code: str, error_message: str) -> Path:
        payload = ErrorPayload(
            caseId=case_id,
            taskName="Check Account Balance",
            dateTime=datetime.utcnow().isoformat(),
            errors=[ErrorEntry(code=error_code, message=error_message)],
        )
        err_file = self._errors_dir / f"{case_id}_error.json"
        err_file.write_text(
            payload.model_dump_json(indent=2),
            encoding="utf-8"
        )
        return err_file
```

When `case_id` is not yet known (parse failed before extracting it), use the source file stem as the fallback identifier, prefixed with `UNKNOWN_`:

```python
case_id = case_id or f"UNKNOWN_{source_file_stem}"
```

Error filename: `<caseId>_error.json` in the `errors/` directory.

### 3. EmitStage — `src/app/pipeline/stages.py`

Replace the stub:

```python
class EmitStage(BaseStage):
    name = "emit"

    def __init__(self, outbox_dir: Path, errors_dir: Path):
        self._output_writer = OutputWriter(outbox_dir)
        self._error_writer = ErrorWriter(errors_dir)

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        if envelope.status == PipelineStatus.ERROR:
            # Write error file
            case_id = (
                envelope.domain_input.caseId  # type: ignore
                if envelope.domain_input else None
            )
            err_file = self._error_writer.write(
                case_id=case_id or f"UNKNOWN_{envelope.source_file.stem}",
                error_code=envelope.error_code or "ERR_UNKNOWN",
                error_message=envelope.error_message or "Unknown error",
            )
            envelope.error_file = err_file
            return envelope  # status remains ERROR

        result: DomainResult = envelope.domain_result  # type: ignore
        if result is None:
            return self._fail(envelope, "ERR_EMIT_NO_RESULT", "domain_result is None")

        try:
            out_file = self._output_writer.write(result)
            envelope.output_file = out_file
            return envelope
        except OSError as e:
            return self._fail(envelope, "ERR_EMIT_WRITE_FAILED", str(e))
```

Note: `EmitStage` is always run, even on error. This means it must check the envelope status at entry and route accordingly. The engine already stops advancing stages once status is `ERROR`, **except** for stages configured to run in the error path. For simplicity in this implementation, move `EmitStage` and `ArchiveStage` after the error path by having the engine skip stages only up to the point of failure and then run a fixed "finalisation" set.

**Simpler alternative (preferred for this spec):** Keep the linear stage list. Accept that `EmitStage` and `ArchiveStage` will receive an error-state envelope and handle it explicitly inside their `execute` methods. The engine does not need to change.

### 4. ArchiveStage — `src/app/pipeline/stages.py`

Replace the stub:

```python
class ArchiveStage(BaseStage):
    name = "archive"

    def __init__(self, archive_dir: Path):
        self._archive_dir = archive_dir

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        try:
            src = envelope.source_file
            if not src.exists():
                # File already moved or doesn't exist — log and continue
                return envelope
            dest = self._archive_dir / src.name
            src.rename(dest)
            return envelope
        except OSError as e:
            # Archive failure is non-fatal: log but do not change status
            logger.warning("Failed to archive %s: %s", envelope.source_file, e)
            return envelope
```

Archive failure must **not** change the envelope status. Losing the archive copy is not critical enough to mark the run as failed.

### 5. Final FileProcessingService update — `src/app/application/services.py`

After `pipeline.run(envelope)` returns, update the database record with the final status and output/error file paths:

```python
final_status = "SUCCESS" if result.status == PipelineStatus.SUCCESS else "ERROR"
with self._uow_factory() as uow:
    uow.records.update_status(
        correlation_id=result.correlation_id,
        status=final_status,
        output_file=str(result.output_file) if result.output_file else None,
        error_details=result.error_message,
        completed_at=result.completed_at,
    )
```

---

## Output format reference

### Successful result (`outbox/<caseId>.json`)

```json
{
  "caseId": "CASE_001",
  "action": "positiveBalance",
  "dateTime": null
}
```

```json
{
  "caseId": "CASE_003",
  "action": "wait",
  "dateTime": "2026-03-25T00:01:00"
}
```

```json
{
  "caseId": "CASE_006",
  "action": "cancel",
  "dateTime": null
}
```

### Error result (`errors/<caseId>_error.json`)

```json
{
  "caseId": "CASE_003",
  "taskName": "Check Account Balance",
  "dateTime": "2026-03-20T10:00:00",
  "errors": [
    {
      "code": "ERR_BALANCE_NOT_FOUND",
      "message": "No balance configured for account: ACC_003"
    }
  ]
}
```

---

## Validations

### V-01 — OutputWriter creates correct file for positive balance

```python
def test_output_writer_positive(tmp_path):
    writer = OutputWriter(tmp_path)
    result = DomainResult(case_id="CASE_001", action=Action.POSITIVE_BALANCE, date_time=None)
    out = writer.write(result)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["caseId"] == "CASE_001"
    assert data["action"] == "positiveBalance"
    assert data["dateTime"] is None
```

### V-02 — OutputWriter sets dateTime for wait action

```python
def test_output_writer_wait(tmp_path):
    writer = OutputWriter(tmp_path)
    dt = datetime(2026, 3, 25, 0, 1, 0)
    result = DomainResult(case_id="CASE_003", action=Action.WAIT, date_time=dt)
    out = writer.write(result)
    data = json.loads(out.read_text())
    assert data["action"] == "wait"
    assert data["dateTime"] == "2026-03-25T00:01:00"
```

### V-03 — ErrorWriter creates error file with correct structure

```python
def test_error_writer(tmp_path):
    writer = ErrorWriter(tmp_path)
    out = writer.write("CASE_001", "ERR_BALANCE_NOT_FOUND", "Balance not found")
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["caseId"] == "CASE_001"
    assert data["taskName"] == "Check Account Balance"
    assert len(data["errors"]) == 1
    assert data["errors"][0]["code"] == "ERR_BALANCE_NOT_FOUND"
```

### V-04 — EmitStage writes outbox file on success

```python
def test_emit_stage_success(tmp_path, envelope_with_domain_result):
    stage = EmitStage(outbox_dir=tmp_path/"outbox", errors_dir=tmp_path/"errors")
    (tmp_path/"outbox").mkdir(); (tmp_path/"errors").mkdir()
    result = stage.execute(envelope_with_domain_result)
    assert result.output_file is not None
    assert result.output_file.exists()
```

### V-05 — EmitStage writes error file when status is ERROR

```python
def test_emit_stage_error_path(tmp_path):
    (tmp_path/"outbox").mkdir(); (tmp_path/"errors").mkdir()
    env = PipelineEnvelope(source_file=Path("inbox/case.json"))
    env.status = PipelineStatus.ERROR
    env.error_code = "ERR_TEST"
    env.error_message = "test error"
    env.failed_stage = "parse"
    stage = EmitStage(outbox_dir=tmp_path/"outbox", errors_dir=tmp_path/"errors")
    result = stage.execute(env)
    assert result.error_file is not None
    assert result.error_file.exists()
    assert result.status == PipelineStatus.ERROR  # status stays ERROR
```

### V-06 — ArchiveStage moves file and does not fail

```python
def test_archive_stage(tmp_path):
    processing = tmp_path / "processing"
    archive = tmp_path / "archive"
    processing.mkdir(); archive.mkdir()
    src = processing / "case_001.json"
    src.write_text("{}")
    env = PipelineEnvelope(source_file=src)
    result = ArchiveStage(archive_dir=archive).execute(env)
    assert not src.exists()
    assert (archive / "case_001.json").exists()
    assert result.status != PipelineStatus.ERROR
```

### V-07 — End-to-end: all six sample cases produce correct actions

Run the full pipeline (with file watcher or direct `pipeline.run()` calls) against the six sample files defined in SPEC-03. Verify:

| File | Expected output action |
|---|---|
| `case_positive.json` | `positiveBalance` |
| `case_zero.json` | `zeroBalance` |
| `case_neg_cli.json` | `wait` (with dateTime) |
| `case_neg_bank.json` | `wait` (with dateTime) |
| `case_wait.json` | `wait` (with existing dateTime) |
| `case_cancel.json` | `cancel` |

```python
def test_end_to_end_all_scenarios(tmp_path):
    # setup, run pipeline for each file, assert outbox file matches expected action
    ...
```

### V-08 — End-to-end: unknown account produces error file

Drop a JSON file referencing `ACC_UNKNOWN` (not in `balances.json`). Verify:
- No file in `outbox/`
- Error file created in `errors/`
- Error file contains `ERR_BALANCE_NOT_FOUND`
- Database record has status `ERROR`

---

## Decisions made

- `EmitStage` handles both success and error paths internally. This avoids needing a two-branch pipeline or special engine logic. The trade-off is that `EmitStage.execute` must inspect the envelope status, which slightly couples it to the engine's failure model. The alternative (separate success/error finalisation) would require engine changes not justified at this scope.
- Archive failure is non-fatal. A failed archive means the source file stays in `processing/`. This is recoverable (the file can be manually moved). It is preferable to logging a warning over marking a successfully processed case as failed.
- Output filenames are based on `caseId`. If two cases with the same `caseId` are processed, the second will overwrite the first. This is acceptable for the simulation use case and matches the idempotent processing model.
- `dateTime` in the output is ISO 8601 format (`"2026-03-25T00:01:00"`) without timezone. The simulation operates in local/naive time. Timezone-aware datetimes can be added later.

---

## References

- Domain models: `madriguera/specs/SPEC-02-domain-models-and-rules.md` — `OutputPayload`, `ErrorPayload`
- Pipeline engine: `madriguera/specs/SPEC-05-pipeline-engine.md`
- Functional specification: `dia5/Especificación funcional - Simulación de proceso automático de verificación de saldo.md` — sections 9, 10
- Architecture guide: `madriguera/architecture-definition.md` — sections "Outbound adapter layer", "Error handling model", "Observability and traceability"
- Process analysis: `dia2/first_analysis/Process.md` — "Output contract", "Error handling"
