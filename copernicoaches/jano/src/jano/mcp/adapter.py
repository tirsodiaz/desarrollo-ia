from fastmcp import FastMCP

from jano.application.convert import convert_file

mcp = FastMCP("jano", instructions="Bidirectional Word ↔ Markdown document converter.")


@mcp.tool()
def convert_document(input_path: str, output_path: str) -> dict:
    """Convert a document between DOCX and Markdown formats.

    Args:
        input_path: Absolute or relative path to the source file (.docx or .md).
        output_path: Absolute or relative path for the output file (.md or .docx).

    Returns:
        A dict with 'success' (bool), 'warnings' (list), and optionally 'error' (str).
    """
    try:
        result = convert_file(input_path, output_path)
        return {
            "success": True,
            "warnings": [
                {"element_type": w.element_type, "description": w.description}
                for w in result.warnings
            ],
            "error": None,
        }
    except Exception as e:
        return {"success": False, "warnings": [], "error": str(e)}


def run_mcp() -> None:
    mcp.run()
