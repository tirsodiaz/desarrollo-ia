"""Tests del modelo de estado."""

from pathlib import Path

import pytest

from miller.state.model import AppState, FileEntry


class TestFileEntry:
    def test_file_entry_creation(self):
        entry = FileEntry(name="readme.md", path=Path("/tmp/readme.md"), is_dir=False)
        assert entry.name == "readme.md"
        assert entry.path == Path("/tmp/readme.md")
        assert entry.is_dir is False

    def test_file_entry_directory(self):
        entry = FileEntry(name="src", path=Path("/tmp/src"), is_dir=True)
        assert entry.is_dir is True

    def test_file_entry_immutable(self):
        entry = FileEntry(name="test.txt", path=Path("/tmp/test.txt"), is_dir=False)
        with pytest.raises(AttributeError):
            entry.name = "other.txt"


class TestAppState:
    def test_app_state_defaults(self):
        state = AppState(current_dir=Path("/"), parent_dir=None)
        assert state.current_dir == Path("/")
        assert state.parent_dir is None
        assert state.current_contents == []
        assert state.selected_index == -1
        assert state.error_message is None

    def test_app_state_with_contents(self):
        entries = [
            FileEntry(name="dir1", path=Path("/dir1"), is_dir=True),
            FileEntry(name="file1.txt", path=Path("/file1.txt"), is_dir=False),
        ]
        state = AppState(
            current_dir=Path("/"),
            parent_dir=None,
            current_contents=entries,
            selected_index=0,
        )
        assert len(state.current_contents) == 2
        assert state.selected_index == 0

    def test_app_state_mutable(self):
        state = AppState(current_dir=Path("/"), parent_dir=None)
        state.selected_index = 3
        assert state.selected_index == 3
        state.error_message = "Error: acceso denegado"
        assert state.error_message == "Error: acceso denegado"
