from __future__ import annotations

import sys

from jano.application.convert import convert_file

USAGE = "Usage: jano <input_file> <output_file>\n"


def run_cli(args: list[str] | None = None) -> int:
    if args is None:
        args = sys.argv[1:]

    if not args or "-h" in args or "--help" in args:
        sys.stdout.write(USAGE)
        sys.stdout.write("\nConvert documents between .docx and .md formats.\n")
        sys.stdout.write("\nExamples:\n")
        sys.stdout.write("  jano input.docx output.md\n")
        sys.stdout.write("  jano input.md output.docx\n")
        return 0

    if len(args) != 2:
        sys.stderr.write(f"Error: expected 2 arguments, got {len(args)}.\n")
        sys.stderr.write(USAGE)
        return 1

    input_path, output_path = args[0], args[1]

    try:
        result = convert_file(input_path, output_path)
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        return 1

    sys.stdout.write(f"Converted: {input_path} → {output_path}\n")
    for w in result.warnings:
        sys.stderr.write(f"[WARN] {w.element_type}: {w.description}\n")

    return 0
