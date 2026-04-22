# DocConv

Bidirectional document converter between Word (.docx) and Markdown (.md) files.

## Features

- Convert Word documents (.docx) to Markdown (.md)
- Convert Markdown files (.md) to Word documents (.docx)
- Command Line Interface (CLI) for direct usage
- MCP (Model Context Protocol) server for AI agent integration
- Preserves document structure and formatting

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone <repository-url>
cd docconv

# Install dependencies
uv sync

# Install the package in development mode
uv pip install -e .
```

## Usage

### Command Line Interface

```bash
# Convert Word to Markdown
docconv convert input.docx output.md

# Convert Markdown to Word
docconv convert input.md output.docx

# Show help
docconv --help
```

### MCP Server

The MCP server allows AI agents to use the document conversion functionality.

```bash
# Start MCP server
docconv mcp
```

## Development

### Setup

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check

# Format code
uv run ruff format
```

### Project Structure

```
src/docconv/
├── cli/           # Command Line Interface
├── mcp/           # MCP Server implementation
├── application/   # Application orchestration layer
├── domain/        # Core business logic and models
└── infrastructure/ # I/O operations and external services

tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
└── e2e/          # End-to-end tests
```

## Architecture

This project follows Clean Architecture principles with a layered approach:

- **Domain Layer**: Pure business logic, Pydantic models, conversion algorithms
- **Application Layer**: Use cases orchestration, service coordination
- **Infrastructure Layer**: File I/O, external service integrations
- **Adapters Layer**: CLI and MCP interfaces

## Requirements

- Python 3.11+
- uv package manager

## License

[License information]