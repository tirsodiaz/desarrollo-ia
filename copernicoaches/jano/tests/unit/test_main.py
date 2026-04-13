"""Tests for main.py dispatch logic."""

import sys
from unittest.mock import MagicMock, patch


def test_main_dispatches_to_cli(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["jano", "--help"])
    mock_cli = MagicMock(return_value=0)
    with patch("jano.cli.adapter.run_cli", mock_cli):
        with patch("sys.exit") as mock_exit:
            from jano.main import main

            main()
            mock_exit.assert_called_with(0)


def test_dunder_main_calls_main(monkeypatch):
    """Ensure __main__.py's if __name__ == '__main__' block is reachable."""
    import runpy
    from unittest.mock import patch

    monkeypatch.setattr(sys, "argv", ["jano", "--help"])
    with patch("jano.main.main") as mock_main:
        runpy.run_module("jano", run_name="__main__", alter_sys=True)
        mock_main.assert_called_once()


def test_main_dispatches_to_mcp(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["jano", "--mcp"])
    mock_mcp = MagicMock()
    with patch("jano.mcp.adapter.run_mcp", mock_mcp):
        from jano.main import main

        main()
        mock_mcp.assert_called_once()
