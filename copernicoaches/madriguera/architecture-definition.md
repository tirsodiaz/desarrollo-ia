# Architecture Guide — Python File-Driven Processing Pipeline

## Purpose

Define guardrails for a Python console application that watches an input directory, processes incoming files through a decoupled internal pipeline, persists state in a local database, and writes results to an output directory. The design must remain modular so business logic, storage, and pipeline stages can evolve independently.

---

## Core architectural intent

The application is a **local file-driven processing engine**.

Its operational model is simple:

* a file appears in an input directory
* the application detects it automatically
* the file is ingested into an internal pipeline
* processing rules are applied
* state and audit information are persisted
* an output artifact is written to an output directory
* failures are written to a dedicated error flow

This is not a web service. It is a long-running console process.

---

## High-level principles

### 1. Pipeline first

The application must be structured around a pipeline abstraction, not around a single script or a single business flow. The pipeline is the stable core. Business operations plug into it.

### 2. File-system driven

The file system is the entry point. New files in the input directory are the trigger for execution. Use an event-driven watcher, not periodic polling as the primary mechanism.

### 3. Business logic must be isolated

Business rules must not be embedded in file watcher code, ORM models, or CLI bootstrap logic. They belong in independent processing components.

### 4. Persistence behind an abstraction

SQLite is the default local database, but the rest of the application must depend on repository and unit-of-work abstractions, not on SQLite-specific code.

### 5. Explicit models at boundaries

All external and internal payloads must use typed schemas. Pydantic models define contracts at pipeline boundaries.

### 6. Replaceability

The application must be designed so that these can be swapped with limited impact:

* database engine
* file format handlers
* business processors
* watcher implementation

---

## Recommended stack

Use standard modern Python tooling.

* **Python**: 3.12+
* **Packaging / dependency management**: `uv` or Poetry
* **CLI**: `Typer`
* **Validation / schemas**: `Pydantic v2`
* **ORM**: `SQLAlchemy 2.x`
* **Migrations**: `Alembic`
* **File watching**: `watchdog`
* **Logging**: standard `logging` or `structlog`
* **Testing**: `pytest`
* **Configuration**: `pydantic-settings`

Do not use framework-heavy solutions. Keep the runtime lean.

---

## Suggested architectural layers

### 1. CLI / runtime layer

Responsible for:

* starting the process
* loading configuration
* wiring dependencies
* launching the file watcher
* clean shutdown

Must not contain business rules.

### 2. Inbound adapter layer

Responsible for:

* detecting new files
* reading file contents
* normalizing metadata
* creating an initial processing command or envelope

This is infrastructure code.

### 3. Pipeline orchestration layer

Responsible for:

* receiving a unit of work
* executing ordered pipeline steps
* routing success, retry, or failure
* invoking business processors
* managing transaction boundaries where needed

This layer coordinates. It does not contain business decisions.

### 4. Business processing layer

Responsible for:

* interpreting domain input
* applying processing rules
* generating domain results
* deciding business outcomes

This layer must be fully decoupled from watcher and storage details.

### 5. Persistence layer

Responsible for:

* storing processing state
* audit trail
* file metadata
* business records if needed

It must expose interfaces such as repositories and unit of work.

### 6. Outbound adapter layer

Responsible for:

* writing output files
* writing error files
* moving or archiving processed inputs
* formatting result payloads

---

## Internal pipeline model

The internal architecture should support multiple reusable stages.

A typical pipeline shape:

1. **Detect**
2. **Ingest**
3. **Parse**
4. **Validate**
5. **Transform**
6. **Process**
7. **Persist**
8. **Emit**
9. **Archive / Fail**

Each stage should be represented as a distinct component with a stable interface.

A stage should:

* accept a typed input object
* return a typed output object
* raise controlled exceptions for failures
* avoid hidden side effects unless it is explicitly an I/O stage

This allows reuse across different business flows.

---

## Domain and processing model

The application should distinguish clearly between:

* **Pipeline envelope**: metadata about the file and processing run
* **Domain input**: the business payload extracted from the file
* **Domain result**: the business outcome after processing
* **Persistence entities**: ORM models for storage
* **Output artifact**: serialized result written to disk

Do not collapse these into one class hierarchy.

Pydantic models should be used for:

* inbound file payloads
* normalized commands
* domain results
* outbound output payloads
* configuration objects

SQLAlchemy models should be used only for persistence concerns.

---

## Database guidance

SQLite is the default local store, but it must not leak into the rest of the system.

### Required approach

* use SQLAlchemy ORM with SQLAlchemy 2.x patterns
* isolate database access behind repositories
* use a unit-of-work abstraction for transaction control
* configure the engine through settings
* keep SQLite-specific pragmas or tuning isolated in infrastructure code

### Minimum persistence concerns

At minimum, persist:

* file ingestion record
* processing status
* timestamps
* error details
* output reference
* optional business metadata for traceability

### Replaceability rule

The application should be able to move from SQLite to PostgreSQL with minimal changes limited to:

* configuration
* engine/session setup
* migrations
* possible SQL dialect nuances

Business logic must remain unchanged.

---

## File watcher guidance

The application must automatically detect files dropped into the input directory.

### Recommended mechanism

Use `watchdog` with an event handler reacting to file creation and, if needed, file move events.

### Important guardrails

* do not process a file before it is fully written
* use a readiness strategy, such as:

  * temporary extension convention
  * atomic rename into input directory
  * short stabilization check on file size / mtime
* ensure idempotency so the same file is not processed twice
* keep watcher code thin; it should only hand off work to the pipeline

### Operational rule

The watcher triggers work. It does not do the work.

---

## Decoupling business operations

Business operations must be plug-in style components.

Define a processor interface along the lines of:

* accepts a normalized domain input
* returns a domain result
* may use repositories through injected abstractions
* has no knowledge of file watcher internals

This allows multiple operations to share the same pipeline framework.

For example, the application could later support:

* balance-check processing
* document transformation
* validation-only runs
* enrichment flows

The pipeline stays the same. Only processors change.

---

## Error handling model

Errors must be explicit and structured.

Distinguish at least:

* **ingestion errors**: unreadable file, unsupported format
* **validation errors**: invalid payload structure
* **processing errors**: business rule failure
* **infrastructure errors**: database or file system failure

Each failure should produce:

* a persisted error record
* a structured log entry
* an output artifact in an error directory or equivalent failure path

Do not allow unstructured tracebacks to be the only failure mechanism.

---

## Observability and traceability

Every processing run should have a correlation identifier.

Track:

* source file name
* detected time
* processing start/end
* pipeline stage reached
* status
* output file path
* error details if applicable

Logs should be structured enough to reconstruct the flow of a single file through the system.

---

## Configuration model

Configuration must be externalized and typed.

Typical settings:

* input directory
* output directory
* error directory
* archive directory
* database URL
* watcher debounce or stabilization settings
* active processor selection
* logging level

Use `pydantic-settings` for configuration loading and validation.

Do not hardcode environment-specific paths in business code.

---

## Testing expectations

The design must support testing at several levels.

### Unit tests

Test:

* pipeline stages
* business processors
* repository behavior behind abstractions
* Pydantic validation rules

### Integration tests

Test:

* SQLite-backed persistence
* file watcher to pipeline handoff
* end-to-end file in / file out behavior

### Contract tests

Test:

* input file schema handling
* output file structure
* repository interface consistency

The architecture should make it possible to test business logic without touching the file system.

---

## Suggested project structure

```text
src/
  app/
    cli/
    config/
    pipeline/
    domain/
    application/
    infrastructure/
      filesystem/
      persistence/
      watcher/
    outputs/
    errors/
tests/
```

A more explicit breakdown:

```text
src/app/
  main.py
  cli/
    commands.py
  config/
    settings.py
  pipeline/
    engine.py
    stages.py
    contracts.py
  domain/
    models.py
    processors.py
    rules.py
  application/
    services.py
    commands.py
    results.py
  infrastructure/
    watcher/
      file_watcher.py
    filesystem/
      readers.py
      writers.py
      archiver.py
    persistence/
      models.py
      repositories.py
      uow.py
      session.py
      migrations/
```

Keep the dependency direction inward:

* infrastructure depends on application/domain
* application depends on domain
* domain depends on nothing external

---

## Non-goals

This guide does not target:

* HTTP APIs
* distributed execution
* cloud-native orchestration
* complex workflow engines
* framework-centric design

Those can be added later if needed. The current system is local, file-driven, modular, and replaceable.

---

## Final implementation guardrails

1. Build a **long-running console process**, not a web app.
2. Use `watchdog` for automatic file detection.
3. Keep the **watcher thin** and route work into a reusable pipeline.
4. Use **Pydantic** for typed contracts at boundaries.
5. Use **SQLAlchemy 2.x + Alembic** for persistence.
6. Hide SQLite behind repository and unit-of-work abstractions.
7. Keep **business processors independent** from watcher and ORM code.
8. Separate:

   * inbound file handling
   * pipeline orchestration
   * domain processing
   * persistence
   * outbound writing
9. Make processing idempotent and failure-aware.
10. Design so the same pipeline framework can support multiple business operations later.

If the AI code generator follows these rules, the result should be a maintainable local processing engine rather than a one-off script.
