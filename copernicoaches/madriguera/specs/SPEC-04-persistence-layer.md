# SPEC-04 — Persistence Layer

## Goal

Implement the persistence layer: SQLAlchemy ORM models, repository abstractions, unit-of-work pattern, and Alembic migrations. Every file-processing run must leave a traceable record in the local SQLite database. Business logic must never import from this layer directly.

---

## Scope

- SQLAlchemy 2.x ORM model for processing runs (`ProcessingRecord`)
- Repository interface and SQLAlchemy implementation
- Unit-of-work abstraction for transaction control
- SQLAlchemy session factory wired from settings
- Alembic configured and initial migration created
- Unit tests for repository behaviour

---

## Deliverables

### 1. ORM model — `src/app/infrastructure/persistence/models.py`

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, Text
from datetime import datetime

class Base(DeclarativeBase):
    pass

class ProcessingRecord(Base):
    __tablename__ = "processing_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    correlation_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    case_id: Mapped[str] = mapped_column(String(128), index=True)
    source_file: Mapped[str] = mapped_column(String(512))
    detected_at: Mapped[datetime] = mapped_column(DateTime)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32))   # PENDING | PROCESSING | SUCCESS | ERROR
    action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_file: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_details: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**Status values:**
- `PENDING` — file detected, not yet processed
- `PROCESSING` — pipeline running
- `SUCCESS` — result written to outbox
- `ERROR` — error written to errors directory

### 2. Repository interface — `src/app/application/ports.py`

Add the following protocol to the existing `ports.py` file (from SPEC-03):

```python
class ProcessingRecordRepository(Protocol):
    def add(self, record: ProcessingRecordCreate) -> None: ...
    def get_by_correlation_id(self, correlation_id: str) -> ProcessingRecordRead | None: ...
    def update_status(self, correlation_id: str, status: str, **kwargs) -> None: ...
    def exists(self, source_file: str) -> bool: ...
```

Define lightweight dataclass DTOs (not ORM objects) for the interface:

```python
from dataclasses import dataclass

@dataclass
class ProcessingRecordCreate:
    correlation_id: str
    case_id: str
    source_file: str
    detected_at: datetime
    status: str = "PENDING"

@dataclass
class ProcessingRecordRead:
    correlation_id: str
    case_id: str
    source_file: str
    detected_at: datetime
    status: str
    action: str | None
    output_file: str | None
    error_details: str | None
```

### 3. SQLAlchemy repository — `src/app/infrastructure/persistence/repositories.py`

```python
class SqlProcessingRecordRepository:
    def __init__(self, session: Session): ...

    def add(self, record: ProcessingRecordCreate) -> None:
        # Insert a new ProcessingRecord ORM object
        ...

    def get_by_correlation_id(self, correlation_id: str) -> ProcessingRecordRead | None:
        # Query by correlation_id, return mapped DTO or None
        ...

    def update_status(self, correlation_id: str, status: str, **kwargs) -> None:
        # Update status and optional extra fields (action, output_file, error_details,
        # started_at, completed_at) by correlation_id
        ...

    def exists(self, source_file: str) -> bool:
        # Return True if a record with this source_file already exists
        # Used for idempotency check
        ...
```

All methods operate on the injected `Session`. They do not commit. Committing is the responsibility of the unit of work.

### 4. Unit of work — `src/app/infrastructure/persistence/uow.py`

```python
class UnitOfWork:
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory
        self.records: SqlProcessingRecordRepository | None = None

    def __enter__(self) -> "UnitOfWork":
        self._session = self._session_factory()
        self.records = SqlProcessingRecordRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            self._session.rollback()
        else:
            self._session.commit()
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
```

Usage pattern:
```python
with uow:
    uow.records.add(record)
# session is committed and closed automatically
```

### 5. Session factory — `src/app/infrastructure/persistence/session.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

def build_session_factory(database_url: str) -> Callable[[], Session]:
    engine = create_engine(database_url, echo=False)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

`create_all_tables(engine)` must be a separate callable that runs `Base.metadata.create_all(engine)`. This is called at startup (CLI layer) before the watcher starts, NOT inside the session factory.

### 6. Alembic setup

Initialise Alembic:
```
alembic init madriguera/alembic
```

Configure `alembic.ini` and `alembic/env.py` to:
- Read `sqlalchemy.url` from `AppSettings.database_url`
- Import `Base` from `app.infrastructure.persistence.models`
- Use `Base.metadata` as the target metadata

Create the initial migration:
```
alembic revision --autogenerate -m "initial schema"
```

Verify the generated migration creates the `processing_records` table with all columns.

---

## Validations

### V-01 — Repository add and retrieve

```python
def test_add_and_retrieve(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    with UnitOfWork(factory) as uow:
        uow.records.add(ProcessingRecordCreate(
            correlation_id="corr-001",
            case_id="CASE_001",
            source_file="inbox/case_001.json",
            detected_at=datetime.utcnow(),
        ))

    with UnitOfWork(factory) as uow:
        record = uow.records.get_by_correlation_id("corr-001")
        assert record is not None
        assert record.case_id == "CASE_001"
        assert record.status == "PENDING"
```

### V-02 — update_status changes status and optional fields

```python
with UnitOfWork(factory) as uow:
    uow.records.update_status(
        "corr-001", "SUCCESS",
        action="positiveBalance",
        output_file="outbox/case_001.json",
        completed_at=datetime.utcnow()
    )

with UnitOfWork(factory) as uow:
    record = uow.records.get_by_correlation_id("corr-001")
    assert record.status == "SUCCESS"
    assert record.action == "positiveBalance"
```

### V-03 — exists returns True for known file, False for unknown

```python
with UnitOfWork(factory) as uow:
    assert uow.records.exists("inbox/case_001.json") is True
    assert uow.records.exists("inbox/never_seen.json") is False
```

### V-04 — Rollback on exception

```python
try:
    with UnitOfWork(factory) as uow:
        uow.records.add(ProcessingRecordCreate(
            correlation_id="corr-002", case_id="X",
            source_file="f.json", detected_at=datetime.utcnow()
        ))
        raise RuntimeError("simulated failure")
except RuntimeError:
    pass

with UnitOfWork(factory) as uow:
    assert uow.records.get_by_correlation_id("corr-002") is None
```

### V-05 — Alembic upgrade head runs without error

```bash
alembic upgrade head
```

Must complete without errors on a fresh SQLite database.

### V-06 — Duplicate correlation_id raises IntegrityError

```python
with pytest.raises(IntegrityError):
    with UnitOfWork(factory) as uow:
        uow.records.add(ProcessingRecordCreate(correlation_id="corr-001", ...))
        # corr-001 already exists
```

---

## Decisions made

- DTOs (`ProcessingRecordCreate`, `ProcessingRecordRead`) are plain dataclasses, not ORM objects. The application layer interacts only with DTOs, never with SQLAlchemy models directly. This enforces the inward dependency rule.
- `update_status` accepts `**kwargs` for optional fields to avoid a proliferation of specific update methods. Accepted keyword arguments are: `action`, `output_file`, `error_details`, `started_at`, `completed_at`.
- `Base.metadata.create_all` is called at CLI startup for simplicity. In a production setup, Alembic migrations would be the only schema management path. Both paths are supported; the create_all call is idempotent.
- The `exists` method checks by `source_file` path (the full file name as seen from the watched directory). This is the idempotency key: the same physical file will never be re-processed even if it reappears.

---

## References

- Architecture guide: `madriguera/architecture-definition.md` — sections "Persistence layer", "Database guidance", "Replaceability rule"
- Architecture guide: `madriguera/architecture-definition.md` — "Observability and traceability"
