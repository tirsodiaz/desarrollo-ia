# Step 08 — MCP Adapter

## Goal
Expose the same conversion capabilities as the CLI via an MCP server using FastMCP. Activated with `--mcp`.

## File
`jano/src/jano/mcp/adapter.py`

## Dependencies
- `fastmcp`
- `jano.application.convert`

## Public interface

```python
def run_mcp() -> None:
    """Start the FastMCP server and serve conversion tools."""
```

## MCP tools to expose

### `convert_document`

```
Tool name:    convert_document
Description:  Convert a document between DOCX and Markdown formats.
Input:
  input_path:  str  — absolute or relative path to the source file
  output_path: str  — absolute or relative path for the output file
Output:
  {
    "success": bool,
    "warnings": [{"element_type": str, "description": str}],
    "error": str | null
  }
```

## Implementation notes
- Use `@mcp.tool()` decorator from FastMCP
- Call `convert_file(input_path, output_path)` from the application layer
- Serialize `ConversionWarning` objects to dicts before returning
- Catch exceptions and return `{"success": false, "error": "<message>"}` instead of raising
- The MCP server MUST NOT implement any conversion logic itself

## Running the MCP server

```bash
uv run python -m jano --mcp
```

The server runs on stdio transport (default FastMCP behavior), compatible with VS Code agent integration.

## Acceptance criteria
- E2E test: start server, call `convert_document` tool with DOCX input, verify output file is created
- E2E test: call `convert_document` with invalid path, verify `success: false` and error message returned
- No conversion logic in this file — only delegation to application layer
