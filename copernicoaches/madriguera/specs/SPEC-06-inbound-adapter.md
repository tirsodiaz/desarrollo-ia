# SPEC-06 — Inbound Adapter: File Watcher & Ingestion Stages

## Goal

Implement the file watcher that detects new JSON files in the inbox directory and the three ingestion pipeline stages (Ingest, Parse, Validate) that turn a raw file into a validated `CaseInput` domain object on the envelope.

---

## Scope

- `watchdog`-based file watcher that hands off detected files to the pipeline
- File stabilisation check to avoid reading files that are still being written
- Idempotency guard: skip files already recorded in the database
- `IngestStage`: reads the file content into `envelope.raw_content`
- `ParseStage`: parses JSON and sets `envelope.domain_input` as a validated `CaseInput`
- `ValidateStage`: performs domain-level validation beyond Pydantic (e.g. contracts list not empty)
- Moving files: inbox → processing on start; processing → archive on success (archive is SPEC-08)

---

## Deliverables

### 1. File watcher — `src/app/infrastructure/watcher/file_watcher.py`

Use `watchdog.observers.Observer` with a custom `FileSystemEventHandler`.

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)

class InboxEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        on_file_ready: Callable[[Path], None],
        stabilisation_seconds: float = 0.5,
    ):
        self._on_file_ready = on_file_ready
        self._stabilisation_seconds = stabilisation_seconds

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".json":
            logger.debug("Ignoring non-JSON file: %s", path.name)
            return
        self._wait_for_stability(path)
        self._on_file_ready(path)

    def _wait_for_stability(self, path: Path) -> None:
        time.sleep(self._stabilisation_seconds)
        # Optional: add a second size-check loop here if needed
```

```python
class FileWatcher:
    def __init__(
        self,
        inbox_dir: Path,
        on_file_ready: Callable[[Path], None],
        stabilisation_seconds: float = 0.5,
    ):
        self._inbox_dir = inbox_dir
        self._handler = InboxEventHandler(on_file_ready, stabilisation_seconds)
        self._observer = Observer()

    def start(self) -> None:
        self._observer.schedule(self._handler, str(self._inbox_dir), recursive=False)
        self._observer.start()
        logger.info("Watcher started on: %s", self._inbox_dir)

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
        logger.info("Watcher stopped.")
```

The `on_file_ready` callback is injected so the watcher has no knowledge of the pipeline.

### 2. Watcher-to-pipeline handoff — `src/app/application/services.py`

Create a `FileProcessingService` that:

1. Receives a `Path` from the watcher callback
2. Checks idempotency using `uow.records.exists(str(source_file))`
3. If already processed: log a warning and return
4. Creates a `PipelineEnvelope(source_file=source_file)`
5. Persists a `PENDING` record using the UoW
6. Calls `pipeline_engine.run(envelope)`
7. Updates the record status to `SUCCESS` or `ERROR` based on the result

```python
class FileProcessingService:
    def __init__(
        self,
        pipeline: PipelineEngine,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self._pipeline = pipeline
        self._uow_factory = uow_factory

    def handle(self, source_file: Path) -> None:
        with self._uow_factory() as uow:
            if uow.records.exists(str(source_file)):
                logger.warning("Skipping already-processed file: %s", source_file.name)
                return
            uow.records.add(ProcessingRecordCreate(
                correlation_id=str(uuid.uuid4()),
                case_id="UNKNOWN",  # updated by ParseStage
                source_file=str(source_file),
                detected_at=datetime.utcnow(),
                status="PENDING",
            ))

        envelope = PipelineEnvelope(source_file=source_file)
        result = self._pipeline.run(envelope)

        with self._uow_factory() as uow:
            uow.records.update_status(
                result.correlation_id,
                result.status.upper(),
                action=getattr(result.domain_result, "action", None),
                output_file=str(result.output_file) if result.output_file else None,
                error_details=result.error_message,
                completed_at=result.completed_at,
            )
```

Note: the `correlation_id` on the persistence record must be synchronised with the one on the envelope. Adjust the flow so both share the same ID (generate it once before creating the record and pass it to the envelope constructor).

### 3. IngestStage — `src/app/pipeline/stages.py`

Replace the stub with a real implementation:

```python
class IngestStage(BaseStage):
    name = "ingest"

    def __init__(self, processing_dir: Path):
        self._processing_dir = processing_dir

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        try:
            # Move file to processing directory
            dest = self._processing_dir / envelope.source_file.name
            envelope.source_file.rename(dest)
            envelope = dataclasses.replace(envelope, source_file=dest)  # or manual update

            # Read content
            envelope.raw_content = dest.read_text(encoding="utf-8")
            return envelope
        except FileNotFoundError as e:
            return self._fail(envelope, "ERR_INGEST_FILE_NOT_FOUND", str(e))
        except OSError as e:
            return self._fail(envelope, "ERR_INGEST_OS_ERROR", str(e))
```

### 4. ParseStage — `src/app/pipeline/stages.py`

```python
class ParseStage(BaseStage):
    name = "parse"

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        if envelope.raw_content is None:
            return self._fail(envelope, "ERR_PARSE_NO_CONTENT", "raw_content is empty")
        try:
            data = json.loads(envelope.raw_content)
            envelope.domain_input = CaseInput.model_validate(data)
            return envelope
        except json.JSONDecodeError as e:
            return self._fail(envelope, "ERR_PARSE_INVALID_JSON", str(e))
        except ValidationError as e:
            return self._fail(envelope, "ERR_PARSE_SCHEMA_VIOLATION", str(e))
```

### 5. ValidateStage — `src/app/pipeline/stages.py`

```python
class ValidateStage(BaseStage):
    name = "validate"

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        case: CaseInput = envelope.domain_input  # type: ignore
        if case is None:
            return self._fail(envelope, "ERR_VALIDATE_NO_INPUT", "domain_input not set")
        if len(case.contracts) == 0:
            return self._fail(envelope, "ERR_VALIDATE_NO_CONTRACTS",
                              "contracts list is empty")
        if not case.contracts[0].contractId.strip():
            return self._fail(envelope, "ERR_VALIDATE_EMPTY_CONTRACT_ID",
                              "contracts[0].contractId is blank")
        return envelope
```

### 6. CLI integration — `src/app/cli/commands.py`

Update the `run` command to wire the watcher to the service:

```python
@app.command()
def run():
    settings = AppSettings()
    # ... setup logging, create dirs ...
    session_factory = build_session_factory(settings.database_url)
    create_all_tables(session_factory().bind)

    uow_factory = lambda: UnitOfWork(session_factory)
    pipeline = build_pipeline(settings=settings)
    service = FileProcessingService(pipeline=pipeline, uow_factory=uow_factory)

    watcher = FileWatcher(
        inbox_dir=settings.inbox_dir,
        on_file_ready=service.handle,
        stabilisation_seconds=settings.file_stabilisation_seconds,
    )
    watcher.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        logger.info("Madriguera stopped.")
```

---

## Validations

### V-01 — IngestStage moves file to processing dir

```python
def test_ingest_stage_moves_file(tmp_path):
    inbox = tmp_path / "inbox"
    processing = tmp_path / "processing"
    inbox.mkdir(); processing.mkdir()

    test_file = inbox / "case_001.json"
    test_file.write_text('{"caseId": "X"}')

    stage = IngestStage(processing_dir=processing)
    env = PipelineEnvelope(source_file=test_file)
    result = stage.execute(env)

    assert result.status != PipelineStatus.ERROR
    assert (processing / "case_001.json").exists()
    assert not test_file.exists()
    assert result.raw_content == '{"caseId": "X"}'
```

### V-02 — IngestStage fails gracefully if file is missing

```python
def test_ingest_stage_missing_file(tmp_path):
    stage = IngestStage(processing_dir=tmp_path)
    env = PipelineEnvelope(source_file=Path("/nonexistent/file.json"))
    result = stage.execute(env)
    assert result.status == PipelineStatus.ERROR
    assert result.error_code == "ERR_INGEST_FILE_NOT_FOUND"
```

### V-03 — ParseStage produces a valid CaseInput

```python
def test_parse_stage_valid_json(sample_case_json):
    stage = ParseStage()
    env = PipelineEnvelope(source_file=Path("x.json"), raw_content=sample_case_json)
    result = stage.execute(env)
    assert result.status != PipelineStatus.ERROR
    assert isinstance(result.domain_input, CaseInput)
    assert result.domain_input.caseId == "CASE_001"
```

### V-04 — ParseStage fails on malformed JSON

```python
def test_parse_stage_bad_json():
    stage = ParseStage()
    env = PipelineEnvelope(source_file=Path("x.json"), raw_content="{not json}")
    result = stage.execute(env)
    assert result.status == PipelineStatus.ERROR
    assert result.error_code == "ERR_PARSE_INVALID_JSON"
```

### V-05 — ValidateStage fails on empty contracts

```python
def test_validate_empty_contracts():
    case = CaseInput(caseId="X", source="CLI", contracts=[],
                     accountClosure=AccountClosure(entity="0014"))
    env = PipelineEnvelope(source_file=Path("x.json"), domain_input=case)
    result = ValidateStage().execute(env)
    assert result.status == PipelineStatus.ERROR
    assert result.error_code == "ERR_VALIDATE_NO_CONTRACTS"
```

### V-06 — Idempotency: second call for same file is skipped

```python
def test_idempotency(tmp_path, uow_factory):
    service = FileProcessingService(pipeline=stub_pipeline, uow_factory=uow_factory)
    file = tmp_path / "test.json"
    file.write_text(valid_case_json)

    # First call: processed
    service.handle(file)
    # Manually re-create the file (simulate re-drop)
    file.write_text(valid_case_json)
    # Second call: skipped
    service.handle(file)

    with uow_factory() as uow:
        # Only one record should exist
        records = uow.records.get_all_for_file(str(file))
        assert len(records) == 1
```

### V-07 — Watcher triggers callback on .json file creation

```python
def test_watcher_detects_json(tmp_path):
    received = []
    watcher = FileWatcher(
        inbox_dir=tmp_path,
        on_file_ready=lambda p: received.append(p),
        stabilisation_seconds=0.1,
    )
    watcher.start()
    (tmp_path / "test.json").write_text("{}")
    time.sleep(0.5)
    watcher.stop()
    assert any(p.name == "test.json" for p in received)
```

---

## Decisions made

- The watcher only handles `.json` files; other extensions are silently ignored.
- File stabilisation is a fixed sleep (`stabilisation_seconds`). For the simulation use case this is sufficient. A size-poll loop can replace it later.
- `FileProcessingService.handle` is synchronous. The watcher runs in a background thread (via `watchdog`), so `handle` is called from that thread. If concurrent processing is needed later, a queue can be inserted between the watcher and the service.
- The idempotency key is the full file path string (relative to project root or absolute — whichever is consistent). Use `str(source_file.resolve())` to normalise.
- `ParseStage` imports `CaseInput` from `app.domain.models`. This is the only import crossing from `pipeline` into `domain`. It is intentional: the parse stage's job is to produce a domain object.

---

## References

- Architecture guide: `madriguera/architecture-definition.md` — sections "Inbound adapter layer", "File watcher guidance"
- Architecture guide: `madriguera/architecture-definition.md` — "Decoupling business operations", "Error handling model"
- Functional specification: `dia5/Especificación funcional - Simulación de proceso automático de verificación de saldo.md` — sections 3, 4, 6
