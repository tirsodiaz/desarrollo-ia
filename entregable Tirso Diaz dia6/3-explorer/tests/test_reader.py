"""Tests de la capa de sistema de archivos."""

import os
from pathlib import Path

import pytest

from miller.filesystem.reader import (
    detect_changes,
    get_parent,
    is_hidden,
    list_directory,
    read_preview,
    TEXT_EXTENSIONS,
)
from miller.state.model import FileEntry


@pytest.fixture
def sample_dir(tmp_path):
    """Crea un directorio con estructura de prueba."""
    # Directorios
    (tmp_path / "Alpha").mkdir()
    (tmp_path / "beta").mkdir()
    # Archivos
    (tmp_path / "charlie.txt").write_text("line1\nline2\nline3\nline4\nline5\nline6", encoding="utf-8")
    (tmp_path / "Delta.py").write_text("print('hello')", encoding="utf-8")
    return tmp_path


@pytest.fixture
def hidden_dir(tmp_path):
    """Crea un directorio con archivos ocultos (dotfiles)."""
    (tmp_path / ".hidden_file").write_text("secret", encoding="utf-8")
    (tmp_path / ".hidden_dir").mkdir()
    (tmp_path / "visible.txt").write_text("visible", encoding="utf-8")
    return tmp_path


@pytest.fixture
def symlink_dir(tmp_path):
    """Crea un directorio con enlaces simbólicos."""
    target = tmp_path / "real_file.txt"
    target.write_text("real", encoding="utf-8")
    link = tmp_path / "link_file.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("No se pueden crear symlinks en este entorno")
    return tmp_path


class TestListDirectory:
    def test_sorts_dirs_first(self, sample_dir):
        entries = list_directory(sample_dir)
        dirs = [e for e in entries if e.is_dir]
        files = [e for e in entries if not e.is_dir]
        # Los directorios deben aparecer antes que los archivos
        if dirs and files:
            last_dir_idx = max(i for i, e in enumerate(entries) if e.is_dir)
            first_file_idx = min(i for i, e in enumerate(entries) if not e.is_dir)
            assert last_dir_idx < first_file_idx

    def test_alphabetical_case_insensitive(self, sample_dir):
        entries = list_directory(sample_dir)
        dirs = [e for e in entries if e.is_dir]
        files = [e for e in entries if not e.is_dir]
        # Directorios: Alpha, beta (case-insensitive)
        dir_names = [d.name for d in dirs]
        assert dir_names == sorted(dir_names, key=str.lower)
        # Archivos: charlie.txt, Delta.py (case-insensitive)
        file_names = [f.name for f in files]
        assert file_names == sorted(file_names, key=str.lower)

    def test_excludes_hidden_dotfiles(self, hidden_dir):
        entries = list_directory(hidden_dir)
        names = [e.name for e in entries]
        assert ".hidden_file" not in names
        assert ".hidden_dir" not in names
        assert "visible.txt" in names

    def test_excludes_symlinks(self, symlink_dir):
        entries = list_directory(symlink_dir)
        names = [e.name for e in entries]
        assert "link_file.txt" not in names
        assert "real_file.txt" in names

    def test_empty_directory(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        entries = list_directory(empty)
        assert entries == []

    def test_permission_error(self, tmp_path):
        restricted = tmp_path / "restricted"
        restricted.mkdir()
        try:
            restricted.chmod(0o000)
            entries = list_directory(restricted)
            assert entries == []
        finally:
            restricted.chmod(0o755)

    def test_returns_file_entries(self, sample_dir):
        entries = list_directory(sample_dir)
        assert all(isinstance(e, FileEntry) for e in entries)
        assert all(isinstance(e.path, Path) for e in entries)


class TestIsHidden:
    def test_dotfile_is_hidden(self):
        assert is_hidden(Path("/tmp/.hidden")) is True

    def test_normal_file_not_hidden(self):
        assert is_hidden(Path("/tmp/visible.txt")) is False

    def test_dot_in_middle_not_hidden(self):
        assert is_hidden(Path("/tmp/file.txt")) is False


class TestReadPreview:
    def test_directory_preview(self, sample_dir):
        preview = read_preview(sample_dir / "Alpha")
        assert isinstance(preview, list)

    def test_text_file_preview(self, sample_dir):
        preview = read_preview(sample_dir / "charlie.txt")
        assert len(preview) == 5
        assert preview[0] == "line1"
        assert preview[4] == "line5"

    def test_text_file_short(self, tmp_path):
        short = tmp_path / "short.txt"
        short.write_text("only two\nlines", encoding="utf-8")
        preview = read_preview(short)
        assert len(preview) == 2

    def test_binary_file_preview(self, tmp_path):
        binary = tmp_path / "image.exe"
        binary.write_bytes(b"\x00\x01\x02")
        preview = read_preview(binary)
        assert preview == ["image.exe"]

    def test_utf8_error_treated_as_binary(self, tmp_path):
        bad = tmp_path / "bad.txt"
        bad.write_bytes(b"\x80\x81\x82\x83")
        preview = read_preview(bad)
        assert preview == ["bad.txt"]

    def test_directory_with_children(self, sample_dir):
        preview = read_preview(sample_dir)
        assert len(preview) > 0


class TestGetParent:
    def test_root_returns_none(self):
        if os.name == "nt":
            root = Path("C:\\")
        else:
            root = Path("/")
        assert get_parent(root) is None

    def test_subdir_returns_parent(self, tmp_path):
        child = tmp_path / "child"
        child.mkdir()
        parent = get_parent(child)
        assert parent == tmp_path


class TestDetectChanges:
    def test_no_changes(self, sample_dir):
        contents = list_directory(sample_dir)
        assert detect_changes(sample_dir, contents) is False

    def test_new_file_detected(self, sample_dir):
        contents = list_directory(sample_dir)
        (sample_dir / "new_file.txt").write_text("new", encoding="utf-8")
        assert detect_changes(sample_dir, contents) is True

    def test_deleted_file_detected(self, sample_dir):
        contents = list_directory(sample_dir)
        (sample_dir / "charlie.txt").unlink()
        assert detect_changes(sample_dir, contents) is True
