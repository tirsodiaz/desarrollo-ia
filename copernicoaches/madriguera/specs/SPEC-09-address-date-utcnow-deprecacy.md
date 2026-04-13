# SPEC-09 — Address `datetime.utcnow()` Deprecation

## Goal

Remove uses of `datetime.utcnow()` from the codebase and standardise timestamp handling on timezone-aware UTC datetimes, while preserving current behaviour and keeping the persistence layer migration explicit.

---

## Context

The project targets Python 3.13. In that runtime, `datetime.utcnow()` is deprecated in favour of timezone-aware UTC timestamps created with `datetime.now(datetime.UTC)`.

Current warnings come from three places:

- `PipelineEnvelope.detected_at` default factory in `src/app/pipeline/contracts.py`
- `started_at` / `completed_at` assignment in `src/app/pipeline/engine.py`
- test fixtures and persistence tests that still construct naive UTC datetimes directly

The current persistence layer stores timestamps in naive SQLAlchemy `DateTime` columns:

- `detected_at`
- `started_at`
- `completed_at`

That means the migration is not just a search-and-replace. The codebase must first decide whether the database will continue storing naive UTC or move to timezone-aware values end to end.

---

## Decision

Standardise on this rule:

- Internal application timestamps must be created as aware UTC datetimes using `datetime.now(datetime.UTC)`.
- Conversion must happen only at boundaries.
- Bare `datetime.now()` must not be used for system timestamps.
- `datetime.utcnow()` must not be used anywhere.

Preferred long-term direction:

- Use aware UTC datetimes across the pipeline, application layer, and persistence layer.

Transitional compatibility rule if persistence remains naive temporarily:

- Generate aware UTC datetimes first.
- Convert explicitly to naive UTC only when writing to legacy naive storage.
- Never create naive local-time datetimes for processing timestamps.

---

## Scope

- Replace deprecated timestamp creation in runtime code
- Replace deprecated timestamp creation in tests
- Define one timestamp policy for pipeline, service, and persistence code
- Make database behaviour explicit instead of implicit
- Add validation so regressions fail fast

## Non-goals

- No change to business decision logic
- No change to JSON payload semantics unless required by explicit UTC formatting rules
- No attempt to infer user-local time zones for display purposes

---

## Deliverables

### 1. Introduce a single timestamp policy

Document and enforce the following conventions:

- `detected_at`, `started_at`, and `completed_at` represent UTC instants
- runtime code creates timestamps with `datetime.now(datetime.UTC)`
- tests use the same convention unless they intentionally verify legacy compatibility
- if a function accepts a timestamp from outside the system, it must either require UTC-aware input or normalise it explicitly

Recommended implementation shape:

```python
from datetime import UTC, datetime

def utc_now() -> datetime:
    return datetime.now(UTC)
```

Using a small helper is preferred because it:

- removes repeated import patterns
- makes future mocking easier
- gives the codebase one place to document policy

### 2. Replace deprecated runtime call sites

Update the pipeline code so these call sites stop producing warnings:

- `PipelineEnvelope.detected_at`
- `PipelineEngine.run()` assignment to `started_at`
- `PipelineEngine.run()` assignment to `completed_at`

The runtime must not mix:

- aware UTC creation in one place
- naive UTC creation in another
- naive local time anywhere

### 3. Replace deprecated test call sites

Update tests to stop manufacturing deprecated timestamps directly.

This includes:

- persistence tests
- fixtures
- any adapter or pipeline tests that create envelopes or records with timestamps

Tests should be aligned with the production timestamp policy. Otherwise the suite will keep passing while silently reintroducing deprecated behaviour.

### 4. Make the persistence strategy explicit

Choose one of the following approaches and implement it consistently.

#### Option A — Preferred: aware UTC end to end

Move persistence to timezone-aware timestamp handling.

Expected characteristics:

- ORM columns are explicitly timezone-aware
- application DTOs continue to hold aware UTC datetimes
- no stripping of `tzinfo` before storage
- values read back from persistence remain semantically UTC

Advantages:

- aligns with Python 3.13 direction
- reduces ambiguity
- avoids accidental local-time bugs

Risks:

- requires verifying SQLite and SQLAlchemy behaviour carefully
- may require a migration strategy for existing rows and test expectations

#### Option B — Transitional: naive UTC storage, aware UTC in application code

Keep the database schema temporarily naive, but make conversions explicit.

Expected characteristics:

- runtime code creates only aware UTC datetimes
- repository layer converts aware UTC to naive UTC before writing
- repository layer reattaches UTC semantics when reading, if needed by the domain contract

Required rule:

- conversion must live only in the persistence boundary

This option is acceptable if the team wants a smaller first step, but it should be treated as an interim state rather than the final policy.

### 5. Add regression guards

Add lightweight guardrails so the warning does not come back later.

Recommended guards:

- a test or lint check that no code under `src/` contains `utcnow(`
- a test or lint check that no code under `src/` uses bare `datetime.now()` for system timestamps
- optional pytest configuration to treat this specific deprecation as an error once the migration is complete

Example command-level validation:

```bash
rg -n "utcnow\\(" src tests
```

If the team wants tests to enforce the rule more aggressively after migration, enable:

```bash
pytest -W error::DeprecationWarning
```

That should happen only after all known warnings are removed or intentionally filtered.

---

## Migration Plan

### Phase 1 — Runtime cleanup

1. Introduce a shared UTC timestamp helper.
2. Replace all production `datetime.utcnow()` usage with aware UTC creation.
3. Keep runtime behaviour unchanged apart from warning removal.

Acceptance criteria:

- no `datetime.utcnow()` remains under `src/`
- the pipeline still records `detected_at`, `started_at`, and `completed_at`
- existing tests still pass

### Phase 2 — Test alignment

1. Replace deprecated timestamp creation in tests and fixtures.
2. Ensure tests do not rely on naive local-time behaviour.

Acceptance criteria:

- no `datetime.utcnow()` remains under `tests/`
- the suite passes without deprecation warnings from project-owned test code

### Phase 3 — Persistence decision

1. Choose Option A or Option B.
2. Implement the repository and model changes needed for that option.
3. Add or update tests covering round-trip timestamp semantics.

Acceptance criteria:

- persistence behaviour is documented and explicit
- stored and retrieved timestamps have one consistent UTC contract
- no silent `tzinfo` loss occurs without a boundary conversion that the code makes obvious

### Phase 4 — Warning hardening

1. Turn timestamp deprecations into failures in CI or local test configuration.
2. Add a search-based or lint-based guard against reintroducing `utcnow()`.

Acceptance criteria:

- future uses of deprecated timestamp creation fail fast

---

## Validation

### V-01 — No deprecated runtime timestamp creation

Search must return no matches under `src/`:

```bash
rg -n "utcnow\\(" src
```

### V-02 — No deprecated test timestamp creation

Search must return no matches under `tests/`:

```bash
rg -n "utcnow\\(" tests
```

### V-03 — Runtime timestamps are UTC by contract

Add tests that verify:

- `PipelineEnvelope.detected_at` is created in UTC
- `PipelineEngine` assigns UTC timestamps to `started_at` and `completed_at`

### V-04 — Persistence round-trip is explicit

Depending on the chosen option, add tests that verify one of:

- aware UTC timestamps round-trip without losing timezone semantics
- or aware UTC timestamps are explicitly converted at the persistence boundary and restored consistently on read

### V-05 — Clean warning run

The test suite should pass without project-owned `datetime.utcnow()` deprecation warnings.

---

## Open Questions

1. Should persistence move directly to timezone-aware storage, or should the repository own a temporary aware-to-naive UTC conversion?
2. Do any external file or JSON contracts require naive timestamps today, or are they currently internal only?
3. Should the codebase expose a single `utc_now()` helper in a shared utility module, or should time creation be injected where determinism matters most?

---

## References

- `src/app/pipeline/contracts.py`
- `src/app/pipeline/engine.py`
- `src/app/infrastructure/persistence/models.py`
- `tests/unit/test_persistence.py`
- `tests/unit/conftest.py`
- Python 3.13 `datetime` deprecation guidance for `utcnow()`
