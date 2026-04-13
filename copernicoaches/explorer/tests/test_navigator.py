"""Tests de la lógica de navegación."""

from pathlib import Path

import pytest

from miller.navigation.navigator import Navigator
from miller.state.model import AppState, FileEntry


@pytest.fixture
def nav():
    return Navigator()


@pytest.fixture
def sample_dir(tmp_path):
    """Crea un directorio con estructura de prueba."""
    (tmp_path / "Alpha").mkdir()
    (tmp_path / "Beta").mkdir()
    (tmp_path / "charlie.txt").write_text("content", encoding="utf-8")
    (tmp_path / "delta.py").write_text("print(1)", encoding="utf-8")
    return tmp_path


@pytest.fixture
def sample_state(sample_dir):
    """Estado con directorio de prueba como actual."""
    from miller.filesystem.reader import get_parent, list_directory

    contents = list_directory(sample_dir)
    return AppState(
        current_dir=sample_dir,
        parent_dir=get_parent(sample_dir),
        current_contents=contents,
        selected_index=0,
    )


class TestInitialize:
    def test_initialize_root(self, nav):
        state = nav.initialize()
        # Ahora inicializa en el nivel de unidades
        assert state.is_at_drives is True
        assert state.parent_dir is None
        assert isinstance(state.current_contents, list)
        # Debe haber al menos una unidad
        assert len(state.current_contents) > 0
        assert state.selected_index == 0


class TestMoveUp:
    def test_decrements(self, nav, sample_state):
        sample_state.selected_index = 2
        state = nav.move_up(sample_state)
        assert state.selected_index == 1

    def test_at_top_stays(self, nav, sample_state):
        sample_state.selected_index = 0
        state = nav.move_up(sample_state)
        assert state.selected_index == 0

    def test_empty_directory(self, nav):
        state = AppState(
            current_dir=Path("/"),
            parent_dir=None,
            current_contents=[],
            selected_index=-1,
        )
        result = nav.move_up(state)
        assert result.selected_index == -1

    def test_clears_error(self, nav, sample_state):
        sample_state.error_message = "Error previo"
        sample_state.selected_index = 1
        state = nav.move_up(sample_state)
        assert state.error_message is None


class TestMoveDown:
    def test_increments(self, nav, sample_state):
        sample_state.selected_index = 0
        state = nav.move_down(sample_state)
        assert state.selected_index == 1

    def test_at_bottom_stays(self, nav, sample_state):
        sample_state.selected_index = len(sample_state.current_contents) - 1
        state = nav.move_down(sample_state)
        assert state.selected_index == len(state.current_contents) - 1

    def test_empty_directory(self, nav):
        state = AppState(
            current_dir=Path("/"),
            parent_dir=None,
            current_contents=[],
            selected_index=-1,
        )
        result = nav.move_down(state)
        assert result.selected_index == -1

    def test_clears_error(self, nav, sample_state):
        sample_state.error_message = "Error previo"
        state = nav.move_down(sample_state)
        assert state.error_message is None


class TestEnterDirectory:
    def test_enters_directory(self, nav, sample_state):
        # El primer elemento debería ser un directorio (Alpha)
        assert sample_state.current_contents[0].is_dir
        old_dir = sample_state.current_dir
        state = nav.enter_directory(sample_state)
        assert state.current_dir == old_dir / "Alpha"
        assert state.parent_dir == old_dir

    def test_file_no_effect(self, nav, sample_state):
        # Buscar un archivo en el contenido
        file_idx = next(
            i for i, e in enumerate(sample_state.current_contents) if not e.is_dir
        )
        sample_state.selected_index = file_idx
        old_dir = sample_state.current_dir
        state = nav.enter_directory(sample_state)
        assert state.current_dir == old_dir

    def test_empty_directory(self, nav, sample_state, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        # Crear estado apuntando al padre de empty
        from miller.filesystem.reader import list_directory

        contents = list_directory(tmp_path)
        # Buscar el directorio empty
        empty_idx = next(i for i, e in enumerate(contents) if e.name == "empty")
        sample_state.current_contents = contents
        sample_state.selected_index = empty_idx
        state = nav.enter_directory(sample_state)
        assert state.current_dir == empty
        assert state.selected_index == -1
        assert state.current_contents == []

    def test_no_selection(self, nav):
        state = AppState(
            current_dir=Path("/"),
            parent_dir=None,
            current_contents=[],
            selected_index=-1,
        )
        result = nav.enter_directory(state)
        assert result.current_dir == Path("/")

    @pytest.mark.skipif(
        __import__("sys").platform == "win32",
        reason="chmod(0o000) no restringe acceso en Windows",
    )
    def test_permission_error(self, nav, tmp_path):
        restricted = tmp_path / "restricted"
        restricted.mkdir()
        restricted.chmod(0o000)
        try:
            entry = FileEntry(name="restricted", path=restricted, is_dir=True)
            state = AppState(
                current_dir=tmp_path,
                parent_dir=None,
                current_contents=[entry],
                selected_index=0,
            )
            result = nav.enter_directory(state)
            assert result.current_dir == tmp_path  # No cambió
            assert result.error_message is not None
        finally:
            restricted.chmod(0o755)


class TestGoParent:
    def test_goes_to_parent(self, nav, sample_state, tmp_path):
        # Primero entrar en Alpha
        state = nav.enter_directory(sample_state)
        assert state.current_dir == tmp_path / "Alpha"
        # Luego volver
        state = nav.go_parent(state)
        assert state.current_dir == tmp_path

    def test_selects_previous_directory(self, nav, sample_state, tmp_path):
        # Entrar en Alpha y volver
        state = nav.enter_directory(sample_state)
        state = nav.go_parent(state)
        # La selección debe estar sobre Alpha
        selected = state.current_contents[state.selected_index]
        assert selected.name == "Alpha"

    def test_at_root_no_effect(self, nav):
        # Cuando estamos en la raíz de una unidad (ej. C:\) sin padre,
        # presionar ← debería llevar al nivel de unidades
        state = AppState(
            current_dir=Path("C:\\") if __import__("sys").platform == "win32" else Path("/"),
            parent_dir=None,
            current_contents=[],
            selected_index=-1,
            is_at_drives=False,
        )
        result = nav.go_parent(state)
        assert result.is_at_drives is True
        # Selected index debería apuntar a la unidad actual

    def test_clears_error(self, nav, sample_state, tmp_path):
        state = nav.enter_directory(sample_state)
        state.error_message = "Error previo"
        state = nav.go_parent(state)
        assert state.error_message is None


class TestRefresh:
    def test_no_changes(self, nav, sample_state):
        old_contents = list(sample_state.current_contents)
        state = nav.refresh(sample_state)
        assert len(state.current_contents) == len(old_contents)

    def test_detects_new_file(self, nav, sample_state, tmp_path):
        old_count = len(sample_state.current_contents)
        (tmp_path / "new_file.txt").write_text("new", encoding="utf-8")
        state = nav.refresh(sample_state)
        assert len(state.current_contents) == old_count + 1

    def test_deleted_selection_adjusts(self, nav, sample_state, tmp_path):
        # Seleccionar el último elemento
        sample_state.selected_index = len(sample_state.current_contents) - 1
        last_entry = sample_state.current_contents[-1]
        # Borrar ese elemento
        if last_entry.is_dir:
            last_entry.path.rmdir()
        else:
            last_entry.path.unlink()
        state = nav.refresh(sample_state)
        assert state.selected_index < len(state.current_contents)
        assert state.selected_index >= 0
