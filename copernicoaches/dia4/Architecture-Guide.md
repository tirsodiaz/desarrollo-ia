# Architecture Guide — CLI Application with Optional MCP Service

## 1. Purpose

This document defines the mandatory architectural standards and toolchain requirements for the implementation of the document conversion system.

The system MUST support:
- A default **CLI execution mode**
- An optional **MCP server mode** activated via `--mcp`

The application MUST be designed as a single executable with a shared core logic and multiple interface adapters.

---

## 2. Technology Options

### 2.1 Option A — Python (**RECOMMENDED**)

Python is the **preferred and recommended implementation language**.

Teams MUST choose Python unless they are unable to do so due to lack of capability.

---

### 2.2 Option B — Node.js / TypeScript (**CONDITIONAL**)

Node.js/TypeScript MAY be used **only if Python is not feasible** for the team.

This option is allowed but NOT preferred.

---

## 3. Core Architectural Principles

The system MUST follow a layered architecture with strict separation of concerns.

The following layers MUST exist:

- **Entrypoint**
- **CLI Adapter**
- **MCP Adapter**
- **Application Layer**
- **Domain / Conversion Logic**
- **Infrastructure Layer**

The system MUST:
- Use a **single codebase**
- Use a **single executable**
- Share **one core logic layer** across all interfaces

The system MUST NOT:
- Duplicate logic between CLI and MCP
- Embed business logic in adapters
- Couple domain logic to infrastructure

---

## 4. Execution Model

The application MUST support the following execution modes:

```bash
# CLI mode (default)
app input.docx output.md

# MCP mode
app --mcp
````

### Requirements

* CLI mode MUST be the default execution path
* MCP mode MUST expose the same capabilities as CLI
* MCP MUST be implemented as an adapter, not as a separate system
* The core conversion logic MUST be identical in both modes

---

## 5. Functional Scope

The system MUST support:

* Word → Markdown conversion
* Markdown → Word conversion

The system MUST:

* Preserve document structure (headings, lists, tables)
* Preserve basic formatting (bold, italic)
* Avoid silent data loss
* Report unsupported or degraded elements

---

## 6. Python Implementation Standard (Option A)

### 6.1 Toolchain (MANDATORY)

The following tools MUST be used:

* **uv** — dependency management, execution, environment
* **FastMCP** — MCP server implementation
* **pytest** — testing
* **Ruff** — linting and formatting

The following rules apply:

* `pip` MUST NOT be used directly
* All commands MUST be executed via `uv`
* `pyproject.toml` MUST be the single source of truth

---

### 6.2 Project Structure

The project MUST follow this structure:

```text
src/
  <package>/
    __main__.py
    main.py
    cli/
    mcp/
    application/
    domain/
    infrastructure/
tests/
```

### Structural Requirements

* The package MUST be executable via `python -m`
* `__main__.py` MUST be the entrypoint
* `main.py` MUST orchestrate execution modes
* CLI and MCP MUST call the same application layer

---

### 6.3 Execution via uv

All commands MUST be executed using uv:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format .
uv run python -m <package>
```

---

### 6.4 Testing Requirements

The system MUST include:

* Unit tests (domain logic)
* Integration tests (infrastructure + adapters)
* End-to-end tests (CLI + MCP)

Coverage requirements:

* Total coverage MUST be high (target ≥ 90%)
* Domain and application layers MUST have the highest coverage

---

### 6.5 Code Quality

The following MUST be enforced:

* Ruff linting MUST pass
* Ruff formatting MUST pass
* Checks MUST be executable via uv

---

## 7. Node.js / TypeScript Standard (Option B)

### 7.1 Toolchain (MANDATORY)

The following tools MUST be used:

* **Corepack** — package manager control
* **pnpm** — dependency management
* **TypeScript**
* **MCP TypeScript SDK (v1.x)**
* **Vitest** — testing
* **Biome** — linting and formatting

---

### 7.2 Project Structure

The project MUST follow this structure:

```text
src/
  main.ts
  cli/
  mcp/
  application/
  domain/
  infrastructure/
tests/
```

### Structural Requirements

* `main.ts` MUST be the entrypoint
* CLI and MCP MUST share the same application logic
* MCP MUST be implemented using the official SDK

---

### 7.3 Execution Model

Example commands:

```bash
corepack enable
pnpm install
pnpm test
pnpm biome check .
pnpm exec tsx src/main.ts
```

---

### 7.4 Testing Requirements

The system MUST include:

* Unit tests
* Integration tests
* End-to-end tests

Coverage requirements:

* Coverage MUST be high (target ≥ 90%)
* Core logic MUST be prioritized

---

### 7.5 Code Quality

The following MUST be enforced:

* Biome checks MUST pass
* Formatting MUST be consistent
* All checks MUST be automated

---

## 8. MCP Integration Requirements

The MCP implementation MUST:

* Expose document conversion as tools
* Use the same application layer as CLI
* Be activatable via `--mcp`
* Not introduce duplicate logic

The MCP server MUST be local and runnable without external dependencies.

---

## 9. Separation of Concerns

The system MUST follow these rules:

* CLI MUST only handle user interaction and argument parsing
* MCP MUST only expose tools
* Application layer MUST orchestrate use cases
* Domain layer MUST implement conversion logic
* Infrastructure MUST handle I/O and external concerns

---

## 10. Verification and Automation

The project MUST support a reproducible validation pipeline.

### Python example

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90
```

### Node example

```bash
corepack enable
pnpm install
pnpm biome check .
pnpm test --coverage
```

---

## 11. Non-Goals

The following are explicitly NOT required:

* Perfect visual fidelity between formats
* Complex UI or frontend
* External hosting of MCP servers
* Framework-heavy implementations

