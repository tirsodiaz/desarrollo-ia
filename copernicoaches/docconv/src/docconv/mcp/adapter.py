"""
MCP (Model Context Protocol) adapter for document conversion.

This module provides an MCP server that exposes document conversion
functionality to AI agents and other MCP clients.
"""

import json
from typing import Any, Dict

from fastmcp import FastMCP

from ..application import convert_file


def run_mcp_server():
    """Run the MCP server for document conversion."""
    app = FastMCP(
        name="Document Converter",
        description="Convert documents between DOCX and Markdown formats"
    )

    @app.tool()
    def convert_document(input_path: str, output_path: str) -> str:
        """
        Convert a document between DOCX and Markdown formats.

        Args:
            input_path: Path to the input file (.docx or .md)
            output_path: Path where to save the output file (.md or .docx)

        Returns:
            JSON string with conversion result containing success status,
            warnings, and error message if applicable.
        """
        result = convert_file(input_path, output_path)

        # Convert result to JSON-serializable format
        response: Dict[str, Any] = {
            "success": result.success,
            "input_path": result.input_path,
            "output_path": result.output_path,
            "warnings": [
                {
                    "element_type": w.element_type,
                    "description": w.description,
                    "position": w.position,
                    "details": w.details
                }
                for w in result.warnings
            ]
        }

        if result.error_message:
            response["error_message"] = result.error_message

        return json.dumps(response, indent=2)

    # Run the MCP server
    app.run()


if __name__ == "__main__":
    run_mcp_server()