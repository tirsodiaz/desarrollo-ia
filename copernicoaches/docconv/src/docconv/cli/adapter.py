"""
Command Line Interface adapter for document conversion.

This module provides a CLI interface that parses command line arguments
and orchestrates document conversion.
"""

import argparse
import sys
from pathlib import Path

from ..application import convert_file


def run_cli() -> int:
    """
    Run the CLI interface for document conversion.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Convert documents between DOCX and Markdown formats",
        prog="docconv"
    )

    parser.add_argument(
        "input_path",
        help="Path to the input file (.docx or .md)"
    )

    parser.add_argument(
        "output_path",
        help="Path where to save the output file (.md or .docx)"
    )

    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Run in MCP server mode (for AI agent integration)"
    )

    args = parser.parse_args()

    # If --mcp is specified, delegate to MCP adapter
    if args.mcp:
        from ..mcp.adapter import run_mcp_server
        run_mcp_server()
        return 0

    # Validate arguments
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        return 1

    # Determine expected conversion direction
    input_ext = input_path.suffix.lower()
    output_ext = output_path.suffix.lower()

    if not ((input_ext == '.docx' and output_ext == '.md') or
            (input_ext == '.md' and output_ext == '.docx')):
        print(f"Error: Unsupported conversion from {input_ext} to {output_ext}", file=sys.stderr)
        print("Supported conversions: .docx -> .md, .md -> .docx", file=sys.stderr)
        return 1

    # Perform conversion
    result = convert_file(str(input_path), str(output_path))

    # Report results
    if result.success:
        print(f"Conversion successful: {input_path} -> {output_path}")
        if result.warnings:
            print(f"Warnings: {len(result.warnings)}", file=sys.stderr)
            for warning in result.warnings:
                print(f"  - {warning.description}", file=sys.stderr)
    else:
        print(f"Conversion failed: {result.error_message}", file=sys.stderr)
        if result.warnings:
            print(f"Additional warnings: {len(result.warnings)}", file=sys.stderr)
            for warning in result.warnings:
                print(f"  - {warning.description}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())