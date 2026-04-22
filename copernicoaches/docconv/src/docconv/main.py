"""
Main entry point for the document converter application.

This module dispatches between CLI and MCP modes based on command line arguments.
"""

import sys

from .cli import run_cli


def main():
    """Main entry point that dispatches to appropriate adapter."""
    # Check if --mcp flag is present
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp":
        # Remove --mcp from args so MCP server gets clean args
        sys.argv.pop(1)
        from .mcp import run_mcp_server
        run_mcp_server()
    else:
        # Run CLI by default
        sys.exit(run_cli())


if __name__ == "__main__":
    main()