# SPEC-05 — Pipeline Engine & Stage Contracts

## Goal

Implement the pipeline infrastructure: the typed envelope that travels through the system, a stage interface, and the engine that orchestrates stage execution in order. The pipeline must route failures to a structured error path without crashing the main process.

---

## Scope

- `PipelineEnvelope`: the typed container that carries a unit of work through the pipeline
- `PipelineStage`: the interface every stage must implement
- `PipelineEngine`: the orchestrator that runs stages in sequence
- Error routing: a stage failure stops the run and triggers the error path
- No business logic in this spec — the engine is a coordination mechanism only

---

## Deliverables

### 1. Pipeline contracts — `src/app/pipeline/contracts.py`

#### `PipelineStatus`

```python
from enum import StrEnum

class PipelineStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
```

#### `PipelineEnvelope`

```python
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime
import uuid

class PipelineEnvelope(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    # Identity
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file: Path

    # Lifecycle
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: PipelineStatus = PipelineStatus.PENDING

    # Payload (populated by stages)
    raw_content: str | None = None          # raw file text, set by ingest stage
    domain_input: object | None = None      # CaseInput, set by parse stage
    domain_result: object | None = None     # DomainResult, set by process stage
    output_file: Path | None = None         # set by emit stage
    error_file: Path | None = None          # set by error emit stage

    # Error tracking
    failed_stage: str | None = None
    error_message: str | None = None
    error_code: str | None = None
```

`domain_input` and `domain_result` use `object` here to avoid a circular import between `pipeline` and `domain`. The pipeline engine does not inspect these fields; stages that need them cast to the proper type.

#### `PipelineStage` protocol — `src/app/pipeline/contracts.py`

```python
from typing import Protocol

class PipelineStage(Protocol):
    name: str   # human-readable stage name, used in error and log messages

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        """
        Accept an envelope, perform work, return a (possibly mutated) envelope.
        Must not raise uncontrolled exceptions.
        On failure, set envelope.status = PipelineStatus.ERROR,
        envelope.failed_stage = self.name, envelope.error_message = <detail>,
        and return the envelope immediately.
        """
        ...
```

A stage **must not raise**. It must set the error fields on the envelope and return it. The engine inspects the status after each stage and stops if it finds `ERROR`.

### 2. Pipeline engine — `src/app/pipeline/engine.py`

```python
import logging
from app.pipeline.contracts import PipelineEnvelope, PipelineStage, PipelineStatus

logger = logging.getLogger(__name__)

class PipelineEngine:
    def __init__(self, stages: list[PipelineStage]):
        self._stages = stages

    def run(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        envelope.status = PipelineStatus.RUNNING
        envelope.started_at = datetime.utcnow()

        for stage in self._stages:
            logger.debug("Stage starting", extra={"stage": stage.name,
                         "correlation_id": envelope.correlation_id})
            envelope = stage.execute(envelope)

            if envelope.status == PipelineStatus.ERROR:
                logger.error("Stage failed", extra={
                    "stage": envelope.failed_stage,
                    "error": envelope.error_message,
                    "correlation_id": envelope.correlation_id,
                })
                envelope.completed_at = datetime.utcnow()
                return envelope

            logger.debug("Stage completed", extra={"stage": stage.name,
                         "correlation_id": envelope.correlation_id})

        envelope.status = PipelineStatus.SUCCESS
        envelope.completed_at = datetime.utcnow()
        return envelope
```

The engine is stateless between runs. A new `PipelineEnvelope` is passed in for each file.

### 3. Stage helper base class — `src/app/pipeline/stages.py`

Provide an optional convenience class that stages may inherit from:

```python
class BaseStage:
    name: str = "unnamed_stage"

    def _fail(self, envelope: PipelineEnvelope, code: str, message: str) -> PipelineEnvelope:
        envelope.status = PipelineStatus.ERROR
        envelope.failed_stage = self.name
        envelope.error_code = code
        envelope.error_message = message
        return envelope
```

Using this is not mandatory. Stages may implement the `PipelineStage` protocol directly.

### 4. Concrete stages stubbed — `src/app/pipeline/stages.py`

Define skeleton implementations of the following stages. They will be fully implemented in SPEC-06, SPEC-07, and SPEC-08. For now they must exist as stubs that pass the envelope through unchanged.

| Stage class | `name` | Implemented in |
|---|---|---|
| `IngestStage` | `"ingest"` | SPEC-06 |
| `ParseStage` | `"parse"` | SPEC-06 |
| `ValidateStage` | `"validate"` | SPEC-06 |
| `ProcessStage` | `"process"` | SPEC-07 |
| `PersistStage` | `"persist"` | SPEC-07 |
| `EmitStage` | `"emit"` | SPEC-08 |
| `ArchiveStage` | `"archive"` | SPEC-08 |

Stub `execute` method:
```python
def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
    return envelope  # no-op stub
```

### 5. Pipeline factory — `src/app/pipeline/engine.py`

Expose a factory function:

```python
def build_pipeline(
    # dependencies injected here in SPEC-06, SPEC-07, SPEC-08
) -> PipelineEngine:
    stages = [
        IngestStage(),
        ParseStage(),
        ValidateStage(),
        ProcessStage(),
        PersistStage(),
        EmitStage(),
        ArchiveStage(),
    ]
    return PipelineEngine(stages)
```

The factory signature will grow as later specs inject real dependencies. At this stage, all stages are stubs.

---

## Validations

### V-01 — Engine runs all stages in order

```python
def test_engine_runs_all_stages():
    execution_order = []

    class TrackingStage:
        def __init__(self, label):
            self.name = label
        def execute(self, envelope):
            execution_order.append(self.name)
            return envelope

    engine = PipelineEngine([TrackingStage("a"), TrackingStage("b"), TrackingStage("c")])
    envelope = PipelineEnvelope(source_file=Path("test.json"))
    result = engine.run(envelope)

    assert execution_order == ["a", "b", "c"]
    assert result.status == PipelineStatus.SUCCESS
```

### V-02 — Engine stops at first failure

```python
def test_engine_stops_on_error():
    execution_order = []

    class FailingStage:
        name = "failing"
        def execute(self, envelope):
            envelope.status = PipelineStatus.ERROR
            envelope.failed_stage = "failing"
            envelope.error_message = "something broke"
            return envelope

    class NeverRunStage:
        name = "never"
        def execute(self, envelope):
            execution_order.append("never")
            return envelope

    engine = PipelineEngine([FailingStage(), NeverRunStage()])
    result = engine.run(PipelineEnvelope(source_file=Path("test.json")))

    assert result.status == PipelineStatus.ERROR
    assert result.failed_stage == "failing"
    assert "never" not in execution_order
```

### V-03 — Envelope carries correlation_id through all stages

```python
def test_correlation_id_preserved():
    class EchoStage:
        name = "echo"
        def execute(self, envelope):
            return envelope

    engine = PipelineEngine([EchoStage()])
    env = PipelineEnvelope(source_file=Path("f.json"))
    original_id = env.correlation_id
    result = engine.run(env)
    assert result.correlation_id == original_id
```

### V-04 — PipelineEnvelope generates unique correlation_ids

```python
def test_unique_correlation_ids():
    ids = {PipelineEnvelope(source_file=Path("f.json")).correlation_id for _ in range(100)}
    assert len(ids) == 100
```

### V-05 — Stub pipeline runs end-to-end without error

```python
def test_stub_pipeline():
    engine = build_pipeline()
    env = PipelineEnvelope(source_file=Path("test.json"))
    result = engine.run(env)
    assert result.status == PipelineStatus.SUCCESS
```

### V-06 — BaseStage._fail sets all error fields correctly

```python
class ConcreteStage(BaseStage):
    name = "test_stage"

stage = ConcreteStage()
env = PipelineEnvelope(source_file=Path("f.json"))
result = stage._fail(env, code="ERR001", message="test error")
assert result.status == PipelineStatus.ERROR
assert result.failed_stage == "test_stage"
assert result.error_code == "ERR001"
assert result.error_message == "test error"
```

---

## Decisions made

- Stages return the envelope rather than mutating a shared mutable object. This makes data flow explicit and avoids hidden side effects.
- Stages must not raise; they must signal failure via the envelope. This ensures the engine is always in control of error routing. An unhandled exception from a stage would bypass the error path and potentially crash the watcher process.
- `domain_input` and `domain_result` are typed as `object` on the envelope to avoid circular imports. Each stage that needs these values casts to the concrete type with a runtime check. An alternative (a `Generic` envelope) was considered but rejected for simplicity.
- `correlation_id` defaults to a UUID4 generated at envelope creation, not at engine entry. This means the ID is available before the engine starts, which is useful for the watcher log.

---

## References

- Architecture guide: `madriguera/architecture-definition.md` — sections "Pipeline orchestration layer", "Internal pipeline model"
- Architecture guide: `madriguera/architecture-definition.md` — "Error handling model"
