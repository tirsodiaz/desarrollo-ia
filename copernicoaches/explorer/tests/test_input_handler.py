"""Tests de captura de teclado."""

import sys
import types

import pytest

from miller.ui.input_handler import _read_key_windows, read_key


def test_read_key_windows_ctrl_c_raises(monkeypatch):
    fake_msvcrt = types.SimpleNamespace(getwch=lambda: "\x03")
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)

    with pytest.raises(KeyboardInterrupt):
        _read_key_windows()


def test_read_key_on_windows_ctrl_c_raises(monkeypatch):
    fake_msvcrt = types.SimpleNamespace(getwch=lambda: "\x03")
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(sys, "platform", "win32")

    with pytest.raises(KeyboardInterrupt):
        read_key()
