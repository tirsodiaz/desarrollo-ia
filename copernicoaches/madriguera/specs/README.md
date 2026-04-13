# Madriguera — Implementation Specs

Eight incremental specs that build the application from scaffold to end-to-end operation.
Each spec is self-contained: an Agent can implement it without reading the source documents,
but references are provided at the end of each file for deeper context.

## Build order

| Spec | What it builds | Depends on |
|---|---|---|
| [SPEC-01](SPEC-01-project-scaffold.md) | Project structure, configuration, CLI skeleton | — |
| [SPEC-02](SPEC-02-domain-models-and-rules.md) | Pydantic models, decision rules, working-day calculator | SPEC-01 |
| [SPEC-03](SPEC-03-config-adapters.md) | File-based balance / calendar / rules adapters + sample data | SPEC-02 |
| [SPEC-04](SPEC-04-persistence-layer.md) | SQLAlchemy ORM, repositories, unit-of-work, Alembic | SPEC-01 |
| [SPEC-05](SPEC-05-pipeline-engine.md) | Pipeline envelope, stage contract, engine orchestrator | SPEC-01 |
| [SPEC-06](SPEC-06-inbound-adapter.md) | File watcher, IngestStage, ParseStage, ValidateStage | SPEC-03, SPEC-04, SPEC-05 |
| [SPEC-07](SPEC-07-business-processor.md) | CheckAccountBalanceProcessor, ProcessStage, PersistStage | SPEC-02, SPEC-03, SPEC-04, SPEC-05 |
| [SPEC-08](SPEC-08-outbound-adapter.md) | EmitStage, ArchiveStage, OutputWriter, ErrorWriter | SPEC-05, SPEC-06, SPEC-07 |

## Key architecture decisions (summary)

- `contracts[0]` (0-indexed) is the primary account — normalised from the 1-indexed diagram notation
- Config files simulate external services (balances, calendar, rules) — no real API calls
- Stages never raise; they signal failure via the envelope `status` field
- Business logic (`domain/`, `application/`) has zero imports from `infrastructure/`
- Archive failure is non-fatal; all other failures are recorded in the database and written to `errors/`

## Source documents

- `madriguera/architecture-definition.md` — architectural constraints and stack
- `dia5/Especificación funcional - Simulación de proceso automático de verificación de saldo.md` — functional spec
- `dia5/Ejecución del caso Check Account Balance.md` — exercise scope and evaluation criteria
- `dia2/first_analysis/Process.md` — original process analysis with decision logic detail
- `dia2/first_analysis/Services.md` — original API contracts (simulated in this implementation)
