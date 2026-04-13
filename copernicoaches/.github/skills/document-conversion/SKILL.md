---
name: document-conversion
description: "Use when converting Word (.docx) to Markdown (.md) or Markdown to Word, preferring MCP conversion and using jano CLI only as a fallback."
argument-hint: "Provide input path and output path, for example: convert docs/spec.docx to docs/spec.md."
user-invocable: true
disable-model-invocation: false
---

# Document Conversion

This skill standardizes bidirectional document conversion:
- Word (.docx) -> Markdown (.md)
- Markdown (.md) -> Word (.docx)

## When To Use
- The user asks to convert between .docx and .md.
- The workspace already contains source files to transform.
- A reliable, reproducible conversion path is needed.

## Required Inputs
- Absolute or workspace-relative input file path.
- Absolute or workspace-relative output file path.

## Primary Method (MCP Only)
1. Validate extension pair:
	- .docx -> .md
	- .md -> .docx
2. Run MCP conversion using the jano MCP tool:
	- `mcp_jano-mcp_convert_document` with:
	  - `input_path`
	  - `output_path`
3. Report MCP result clearly:
	- `success`
	- any `warnings`
	- `error` when present

## Fallback Method (Only If MCP Fails)
Use jano CLI as the sole fallback. Do not use other converters.

Allowed command patterns:
- `jano <input_path> <output_path>`
- `uv run python -m jano <input_path> <output_path>`

Fallback rules:
- Execute fallback only after MCP returns failure or an explicit error.
- Preserve the same input and output paths used in MCP attempt.
- Capture and report command result, stderr/stdout summary, and exit code.
- Do not use unsupported subcommands or flags (for example, `convert`, `--input`, `--output`).

## Strict Guardrails
- Prefer MCP every time. Never skip MCP as first attempt.
- Do not use pandoc, python-docx scripts, ad-hoc parsers, or any non-jano fallback.
- Do not change file contents manually to simulate conversion.
- Do not alter unrelated files.

## Output Contract
Always return:
- Conversion direction (.docx -> .md or .md -> .docx)
- Input path and output path
- Method used (MCP or jano fallback)
- Final status (success/failure)
- Warnings or errors

