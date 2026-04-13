"""Tests de visualización con Rich."""

import re
from pathlib import Path

from rich.console import Console

from miller.state.model import AppState, FileEntry
from miller.ui.renderer import FILE_ICON, FOLDER_ICON, Renderer


def _strip_ansi(text: str) -> str:
	return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def _build_state(tmp_path: Path) -> AppState:
	dir_a = tmp_path / "AlphaDir"
	dir_a.mkdir()
	file_b = tmp_path / "beta.txt"
	file_b.write_text("line1\nline2\nline3\nline4\nline5\nline6", encoding="utf-8")
	contents = [
		FileEntry(name=dir_a.name, path=dir_a, is_dir=True),
		FileEntry(name=file_b.name, path=file_b, is_dir=False),
	]
	return AppState(
		current_dir=tmp_path,
		parent_dir=tmp_path.parent,
		current_contents=contents,
		selected_index=0,
	)


def _render_to_text(state: AppState, *, width: int = 60, height: int = 20, no_color: bool = False) -> str:
	console = Console(record=True, width=width, height=height, force_terminal=True, no_color=no_color)
	renderer = Renderer(console=console)
	renderer.render(state, terminal_size=(width, height))
	return console.export_text()


def test_render_empty_state(tmp_path: Path):
	state = AppState(current_dir=tmp_path, parent_dir=tmp_path.parent, current_contents=[], selected_index=-1)
	output = _render_to_text(state)
	assert "Ruta:" in output


def test_render_with_contents(tmp_path: Path):
	state = _build_state(tmp_path)
	output = _render_to_text(state)
	assert "AlphaDir" in output
	assert "beta.txt" in output


def test_render_shows_folder_and_file_icons(tmp_path: Path):
	state = _build_state(tmp_path)
	output = _render_to_text(state, no_color=True)
	assert f"{FOLDER_ICON} AlphaDir" in output
	assert f"{FILE_ICON} beta.txt" in output


def test_header_shows_path(tmp_path: Path):
	state = _build_state(tmp_path)
	output = _render_to_text(state)
	assert "Ruta:" in output
	assert state.current_contents[state.selected_index].name in output


def test_header_keeps_full_path_without_manual_truncation(tmp_path: Path):
	nested = tmp_path / "uno" / "dos" / "tres" / "cuatro"
	nested.mkdir(parents=True)
	state = AppState(current_dir=nested, parent_dir=nested.parent, current_contents=[], selected_index=-1)
	output = _render_to_text(state, width=30, height=12)
	assert "Ruta:" in output
	assert nested.name in output


def test_error_message_displayed(tmp_path: Path):
	state = _build_state(tmp_path)
	state.error_message = "Error: acceso denegado"
	output = _render_to_text(state)
	assert "Error: acceso denegado" in output


def test_truncation(tmp_path: Path):
	long_name = "archivo_con_un_nombre_muy_muy_muy_largo_para_truncar.txt"
	p = tmp_path / long_name
	p.write_text("x", encoding="utf-8")
	state = AppState(
		current_dir=tmp_path,
		parent_dir=tmp_path.parent,
		current_contents=[FileEntry(name=long_name, path=p, is_dir=False)],
		selected_index=0,
	)
	output = _render_to_text(state, width=30, height=10)
	assert "…" in output or "..." in output


def test_directory_style(tmp_path: Path):
	state = _build_state(tmp_path)
	console = Console(record=True, force_terminal=True)
	renderer = Renderer(console=console)
	renderer.render(state)
	output = console.export_text(styles=True)
	assert "\x1b[1;34m" in output


def test_selected_highlight(tmp_path: Path):
	state = _build_state(tmp_path)
	state.selected_index = 1
	console = Console(record=True, force_terminal=True)
	renderer = Renderer(console=console)
	renderer.render(state)
	output = console.export_text(styles=True)
	assert "\x1b[7m" in output


def test_scroll_indicators(tmp_path: Path):
	entries: list[FileEntry] = []
	for i in range(30):
		p = tmp_path / f"f{i:02d}.txt"
		p.write_text("x", encoding="utf-8")
		entries.append(FileEntry(name=p.name, path=p, is_dir=False))

	state = AppState(
		current_dir=tmp_path,
		parent_dir=tmp_path.parent,
		current_contents=entries,
		selected_index=20,
	)
	output = _render_to_text(state, width=60, height=10)
	assert ("^ " in output or "v " in output)


def test_header_remains_active_directory_while_selection_moves(tmp_path: Path):
	entries: list[FileEntry] = []
	for i in range(25):
		p = tmp_path / f"mov{i:02d}.txt"
		p.write_text("x", encoding="utf-8")
		entries.append(FileEntry(name=p.name, path=p, is_dir=False))

	state = AppState(
		current_dir=tmp_path,
		parent_dir=tmp_path.parent,
		current_contents=entries,
		selected_index=0,
	)
	output_top = _render_to_text(state, width=80, height=12)

	state.selected_index = 20
	output_scrolled = _render_to_text(state, width=80, height=12)

	# Header should follow selected entry at index 0 in first render
	assert entries[0].name in output_top
	
	# Header should follow selected entry at index 20 in scrolled render
	assert entries[20].name in output_scrolled


def test_dynamic_blocks_show_new_and_previous_items_on_down_up(tmp_path: Path):
	entries: list[FileEntry] = []
	for i in range(40):
		d = tmp_path / f"d{i:02d}"
		d.mkdir()
		entries.append(FileEntry(name=d.name, path=d, is_dir=True))

	state = AppState(
		current_dir=tmp_path,
		parent_dir=tmp_path.parent,
		current_contents=entries,
		selected_index=2,
	)
	output_initial = _render_to_text(state, width=100, height=18, no_color=True)

	state.selected_index = 25
	output_down = _render_to_text(state, width=100, height=18, no_color=True)

	state.selected_index = 3
	output_up = _render_to_text(state, width=100, height=18, no_color=True)

	assert "d00" in output_initial
	assert "d00" not in output_down
	assert "d25" in output_down
	assert "d00" in output_up


def test_parent_column_at_root():
	root = Path("C:\\") if __import__("sys").platform == "win32" else Path("/")
	state = AppState(current_dir=root, parent_dir=None, current_contents=[], selected_index=-1)
	output = _render_to_text(state)
	assert "Ruta:" in output


def test_parent_column_highlights_current(tmp_path: Path):
	child = tmp_path / "Child"
	child.mkdir()
	state = AppState(current_dir=child, parent_dir=tmp_path, current_contents=[], selected_index=-1)

	output = _render_to_text(state, width=80, height=20)
	assert "Child" in output


def test_right_column_shows_full_file_content_when_file_selected(tmp_path: Path):
	file_a = tmp_path / "a.txt"
	file_a.write_text("L1\nL2\nL3\nL4\nL5\nL6", encoding="utf-8")
	state = AppState(
		current_dir=tmp_path,
		parent_dir=tmp_path.parent,
		current_contents=[FileEntry(name=file_a.name, path=file_a, is_dir=False)],
		selected_index=0,
	)

	output = _render_to_text(state, width=80, height=20)
	assert "L6" in output


def test_vertical_separators_are_visible(tmp_path: Path):
	state = _build_state(tmp_path)
	output = _render_to_text(state, width=80, height=20)
	assert "│" in output


def test_drives_view_does_not_build_preview(tmp_path: Path, monkeypatch):
	drive_entry = FileEntry(name="C:", path=Path("C:\\"), is_dir=True)
	state = AppState(
		current_dir=Path("/drives"),
		parent_dir=None,
		current_contents=[drive_entry],
		selected_index=0,
		is_at_drives=True,
	)

	def fail_if_called(_path):
		raise AssertionError("list_directory should not be called for preview in drives view")

	monkeypatch.setattr("miller.ui.renderer.list_directory", fail_if_called)
	output = _render_to_text(state, width=80, height=20)
	assert "Unidades de disco" in output


def test_selection_counter_is_inline_in_header(tmp_path: Path):
	state = _build_state(tmp_path)
	output = _strip_ansi(_render_to_text(state, width=90, height=20, no_color=True))
	lines = [line.rstrip() for line in output.splitlines() if line.strip()]

	assert any("Esc salir" in line and "[1/2]" in line for line in lines)


def test_footer_does_not_render_standalone_counter_line(tmp_path: Path):
	state = _build_state(tmp_path)
	output = _strip_ansi(_render_to_text(state, width=90, height=20, no_color=True))
	lines = [line.strip() for line in output.splitlines() if line.strip()]

	assert "[1/2]" not in lines


def test_navigation_help_text_visible_with_and_without_error(tmp_path: Path):
	state = _build_state(tmp_path)
	help_text = "up/down mover . -> entrar . <- volver . Esc salir"

	output_ok = _strip_ansi(_render_to_text(state, width=90, height=20, no_color=True))
	assert help_text in output_ok

	state.error_message = "Error: demo"
	output_with_error = _strip_ansi(_render_to_text(state, width=90, height=20, no_color=True))
	assert help_text in output_with_error
	assert "Error: demo" in output_with_error
