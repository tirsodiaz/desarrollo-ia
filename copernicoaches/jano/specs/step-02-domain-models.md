# Step 02 — Domain Models

## Goal
Define the core data structures used across all layers. No I/O, no external dependencies.

## File
`jano/src/jano/domain/models.py`

## Content

### `ConversionDirection`
An enum with two values:
- `DOCX_TO_MD`
- `MD_TO_DOCX`

### `ConversionWarning`
A dataclass with:
- `element_type: str` — type of element that could not be fully preserved (e.g. `"image"`, `"table_border"`)
- `description: str` — human-readable explanation

### `ConversionResult`
A dataclass with:
- `content: str | bytes` — the converted output (str for Markdown, bytes for DOCX)
- `warnings: list[ConversionWarning]` — list of degraded or unsupported elements

## Notes
- All domain types must be pure Python dataclasses or enums
- No imports from application, infrastructure, cli, or mcp layers
- This file is the single source of truth for shared types

## Acceptance criteria
- Models importable with `from jano.domain.models import ConversionResult, ConversionWarning, ConversionDirection`
- No external dependencies required to import this file
