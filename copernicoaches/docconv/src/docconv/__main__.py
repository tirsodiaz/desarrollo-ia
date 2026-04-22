"""
Entry point for running the document converter as a module.

Usage:
    python -m docconv input.docx output.md
    python -m docconv --mcp
"""

from .main import main

if __name__ == "__main__":
    main()