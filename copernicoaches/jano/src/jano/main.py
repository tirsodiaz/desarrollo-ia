import sys


def main() -> None:
    if "--mcp" in sys.argv:
        from jano.mcp.adapter import run_mcp

        run_mcp()
    else:
        from jano.cli.adapter import run_cli

        sys.exit(run_cli())
