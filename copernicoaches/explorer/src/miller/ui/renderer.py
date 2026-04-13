"""Visualización con Rich para Miller Columns."""

from __future__ import annotations

from dataclasses import dataclass

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.table import Table
from rich.text import Text

from miller.filesystem.reader import list_directory
from miller.state.model import AppState, FileEntry

FOLDER_ICON = "\U0001f4c1"  # 📁
FILE_ICON = "\U0001f4c4"    # 📄
NAV_HINT_TEXT = "up/down mover . -> entrar . <- volver . Esc salir"


@dataclass
class Renderer:
	"""Renderiza el estado en consola sin modificarlo."""

	console: Console

	def __init__(self, console: Console | None = None) -> None:
		# Crear consola con legacy_windows=False para evitar problemas de encoding
		self.console = console or Console(legacy_windows=False, force_terminal=True)

	def render(self, state: AppState, terminal_size: tuple[int, int] | None = None) -> None:
		render(state, terminal_size=terminal_size, console=self.console)


def render(
	state: AppState,
	terminal_size: tuple[int, int] | None = None,
	console: Console | None = None,
) -> None:
	"""Renderiza el estado completo en consola."""
	import sys
	import os
	
	# Crear una nueva consola limpia cada render para evitar buffer acumulado
	active_console = console or Console(file=sys.stdout, legacy_windows=False, force_terminal=True)
	
	# En modo interactivo: os.system("cls") es el único método garantizado en Windows/PowerShell
	# Los escape ANSI (\033[H\033[2J) no funcionan si VT processing no está activo en el handle
	if terminal_size is None:
		os.system("cls" if sys.platform == "win32" else "clear")
		# Best-effort clear scrollback where VT is supported.
		active_console.file.write("\033[3J")
		active_console.file.flush()
	width, height = terminal_size or (active_console.size.width, active_console.size.height)
	width = max(30, width)
	height = max(8, height)

	# Calcular footer_size: 1 línea para ayuda + 1 para error (si hay)
	footer_size = 1
	if state.error_message:
		footer_size += 1
	
	header_size = 3
	# Body = total - header - footer
	body_height = height - header_size - footer_size
	# Table SQUARE borders take 2 lines (top + bottom)
	list_height = max(3, body_height - 2)

	left_width, center_width, right_width = _calculate_column_widths(width)

	selected_entry = _get_selected_entry(state)
	header = _build_header(state, selected_entry, width)

	center_lines = _entries_to_lines(
		state.current_contents,
		selected_index=state.selected_index,
		current_dir_name=None,
		width=center_width,
		no_color=active_console.no_color,
	)
	left_lines, left_highlighted_idx = _left_column_data(
		state=state,
		width=left_width,
		no_color=active_console.no_color,
	)

	if state.is_at_drives:
		preview_lines = [Text("(-> para explorar)", style="dim")]
	else:
		preview_lines = _preview_to_lines(
			selected_entry,
			width=right_width,
			no_color=active_console.no_color,
		)

	left_window = _window_with_indicators(left_lines, list_height, left_highlighted_idx)
	center_window = _window_with_indicators(center_lines, list_height, state.selected_index)
	right_window = _window_with_indicators(preview_lines, list_height, None)

	# Table with vertical separators — ratio-based for dynamic resizing
	table = Table(show_header=False, box=box.SQUARE, expand=True, padding=(0, 1))
	table.add_column(ratio=1, no_wrap=True, overflow="ellipsis")  # 20% izquierda
	table.add_column(ratio=2, no_wrap=True, overflow="ellipsis")  # 40% centro
	table.add_column(ratio=2, no_wrap=True, overflow="ellipsis")  # 40% derecha
	table.add_row(left_window, center_window, right_window)

	# Footer
	help_line = Text(NAV_HINT_TEXT, style="dim")
	if state.current_contents and 0 <= state.selected_index < len(state.current_contents):
		position = state.selected_index + 1
		total = len(state.current_contents)
		help_line.append(f" [{position}/{total}]", style="dim")
	footer_parts = [help_line]
	
	if state.error_message:
		footer_parts.append(Text(state.error_message, style="bold red"))
	footer = Text("\n").join(footer_parts)

	# Layout guarantees header and footer are always visible
	layout = Layout(size=height)
	layout.split_column(
		Layout(name="header", size=header_size),
		Layout(name="body"),
		Layout(name="footer", size=footer_size),
	)
	layout["header"].update(header)
	layout["body"].update(table)
	layout["footer"].update(footer)

	# Imprimir layout sin newline final: el \n extra causa scroll en terminales
	active_console.print(layout, end="")
	active_console.file.flush()


def _get_selected_entry(state: AppState) -> FileEntry | None:
	if 0 <= state.selected_index < len(state.current_contents):
		return state.current_contents[state.selected_index]
	return None


def _build_header(
	state: AppState,
	selected_entry: FileEntry | None,
	width: int,
) -> Text:
	max_width = max(1, width - 1)

	def _fit_single_line(text: str) -> str:
		if len(text) <= max_width:
			return text

		if text.startswith("Ruta: "):
			prefix = "Ruta: "
			path = text[len(prefix):]
			available = max_width - len(prefix)
			if available <= 1:
				return text[:max_width]
			# Keep the end of path visible (usually selected file/folder name).
			return prefix + "…" + path[-(available - 1):]

		return text[: max(0, max_width - 1)] + "…"

	if state.is_at_drives:
		return Text("\n\n" + _fit_single_line("Unidades de disco"), style="bold")
	# Si hay una entrada seleccionada, mostrar su ruta
	if selected_entry is not None:
		return Text("\n\n" + _fit_single_line("Ruta: " + str(selected_entry.path)), style="bold")
	# Si no hay selección (lista vacía), mostrar la ruta actual
	return Text("\n\n" + _fit_single_line("Ruta: " + str(state.current_dir)), style="bold")


def _calculate_column_widths(total_width: int) -> tuple[int, int, int]:
	left = max(8, int(total_width * 0.20))
	center = max(8, int(total_width * 0.40))
	right = max(8, total_width - left - center)
	return left, center, right


def _left_column_data(
	state: AppState,
	width: int,
	no_color: bool,
) -> tuple[list[Text], int | None]:
	left_entries: list[FileEntry] = []
	left_highlight_name: str | None = None

	if state.is_at_drives:
		left_entries = []
		left_highlight_name = None
	elif state.parent_dir is not None:
		left_entries = list_directory(state.parent_dir)
		left_highlight_name = state.current_dir.name
	elif not state.is_at_drives:
		from miller.filesystem.reader import list_drives

		left_entries = list_drives()
		drive_name = state.current_dir.drive if state.current_dir.drive else state.current_dir.name
		left_highlight_name = drive_name

	lines = _entries_to_lines(
		left_entries,
		selected_index=None,
		current_dir_name=left_highlight_name,
		width=width,
		no_color=no_color,
	)

	# Find the index of the highlighted entry for scrolling
	highlighted_idx: int | None = None
	if left_highlight_name:
		for i, entry in enumerate(left_entries):
			if entry.name == left_highlight_name:
				highlighted_idx = i
				break

	return lines, highlighted_idx

def _file_content_to_lines(path, width: int) -> list[Text]:
	try:
		with open(path, "r", encoding="utf-8") as file_obj:
			raw_lines = file_obj.read().splitlines()[:20]  # Solo primeras 20 líneas
	except UnicodeDecodeError:
		return [Text("Contenido no textual", style="dim")]
	except (PermissionError, OSError) as exc:
		return [Text(f"Error: {exc}", style="bold red")]

	if not raw_lines:
		return [Text("(archivo vacío)", style="dim")]

	result: list[Text] = []
	for raw_line in raw_lines:
		line = Text(raw_line)
		line.truncate(max(1, width - 1), overflow="ellipsis")
		result.append(line)
	return result


def _entries_to_lines(
	entries: list[FileEntry],
	selected_index: int | None,
	current_dir_name: str | None,
	width: int,
	no_color: bool,
) -> list[Text]:
	lines: list[Text] = []
	for index, entry in enumerate(entries):
		icon = FOLDER_ICON if entry.is_dir else FILE_ICON
		# Size only for directories
		size_label = _format_size(entry) if entry.is_dir else ""
		is_selected = (selected_index is not None and index == selected_index)
		is_highlighted = (current_dir_name and entry.is_dir and entry.name == current_dir_name)

		if no_color:
			prefix = f"{icon} "
			if is_selected or is_highlighted:
				prefix = "> " + prefix
			label = f"{prefix}{entry.name}"
			if size_label:
				label += f" {size_label}"
			line = Text(label)
		else:
			line = Text()
			line.append(f"{icon} ", style="bold blue" if entry.is_dir else "dim")
			line.append(entry.name, style="bold blue" if entry.is_dir else "")
			if size_label:
				line.append(f" {size_label}", style="grey70")
			if is_selected or is_highlighted:
				line.stylize("reverse")

		line.truncate(max(1, width - 1), overflow="ellipsis")
		lines.append(line)
	return lines


def _format_size(entry: FileEntry) -> str:
	if entry.size_bytes is None:
		return ""
	size = float(entry.size_bytes)
	units = ["B", "KB", "MB", "GB", "TB"]
	for unit in units:
		if size < 1024 or unit == units[-1]:
			if unit == "B":
				return f"({int(size)} {unit})"
			return f"({size:.1f} {unit})"
		size /= 1024
	return ""


def _preview_to_lines(selected_entry: FileEntry | None, width: int, no_color: bool) -> list[Text]:
	if selected_entry is None:
		return []

	lines: list[Text] = []
	
	# Si es un directorio, listar sus hijos con estilos
	if selected_entry.is_dir:
		children = list_directory(selected_entry.path)
		for entry in children:
			icon = FOLDER_ICON if entry.is_dir else FILE_ICON
			# Size only for directories, in light gray
			size_label = _format_size(entry) if entry.is_dir else ""
			if no_color:
				prefix = f"{icon} "
				label = f"{prefix}{entry.name}"
				if size_label:
					label += f" {size_label}"
				text = Text(label)
			else:
				text = Text()
				text.append(f"{icon} ", style="bold blue" if entry.is_dir else "dim")
				text.append(entry.name, style="bold blue" if entry.is_dir else "")
				if size_label:
					text.append(f" {size_label}", style="grey70")
			text.truncate(max(1, width - 1), overflow="ellipsis")
			lines.append(text)
	else:
		# Para archivos, mostrar contenido completo en columna derecha
		lines.append(Text(selected_entry.name, style="dim"))
		lines.append(Text(""))
		lines.extend(_file_content_to_lines(selected_entry.path, width))
	
	return lines


def _window_with_indicators(lines: list[Text], visible_height: int, selected_index: int | None) -> Text:
	if visible_height <= 0:
		return Text("")
	if not lines:
		return Text("\n").join([Text("") for _ in range(visible_height)])

	if len(lines) <= visible_height:
		padded = list(lines)
		while len(padded) < visible_height:
			padded.append(Text(""))
		return Text("\n").join(padded)

	start = 0
	if selected_index is not None and selected_index >= 0:
		if selected_index >= visible_height:
			start = selected_index - visible_height + 1
		max_start = max(0, len(lines) - visible_height)
		start = min(start, max_start)

	end = min(len(lines), start + visible_height)
	window = lines[start:end]

	if start > 0:
		window[0] = Text("^ ") + window[0]
	if end < len(lines):
		window[-1] = Text("v ") + window[-1]

	while len(window) < visible_height:
		window.append(Text(""))

	return Text("\n").join(window)
