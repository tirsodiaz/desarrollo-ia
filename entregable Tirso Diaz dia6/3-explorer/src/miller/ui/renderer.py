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


@dataclass
class Renderer:
	"""Renderiza el estado en consola sin modificarlo."""

	console: Console

	def __init__(self, console: Console | None = None) -> None:
		self.console = console or Console()

	def render(self, state: AppState, terminal_size: tuple[int, int] | None = None) -> None:
		render(state, terminal_size=terminal_size, console=self.console)


def render(
	state: AppState,
	terminal_size: tuple[int, int] | None = None,
	console: Console | None = None,
) -> None:
	"""Renderiza el estado completo en consola."""
	active_console = console or Console()
	active_console.clear(home=True)
	width, height = terminal_size or (active_console.size.width, active_console.size.height)
	width = max(30, width)
	height = max(8, height)

	# Footer: 1 line for legend + 1 for error if present
	footer_size = 2 if state.error_message else 1
	# Body = total - header(1) - footer
	body_height = height - 1 - footer_size
	# Table SQUARE borders take 2 lines (top + bottom)
	list_height = max(3, body_height - 2)

	left_width, center_width, right_width = _calculate_column_widths(width)

	selected_entry = _get_selected_entry(state)

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

	preview_lines = _preview_to_lines(
		selected_entry,
		width=right_width,
		no_color=active_console.no_color,
	)

	left_window = _window_with_indicators(left_lines, list_height, left_highlighted_idx)
	center_window = _window_with_indicators(center_lines, list_height, state.selected_index)
	right_window = _window_with_indicators(preview_lines, list_height, None)

	# Header
	if state.is_at_drives:
		header = Text("Unidades de disco", style="bold")
	else:
		path_str = str(state.current_dir)
		prefix = "Ruta: "
		max_path_len = width - len(prefix) - 1
		if len(path_str) > max_path_len > 1:
			path_str = "…" + path_str[-(max_path_len - 1):]
		header = Text(prefix + path_str, style="bold")

	# Table with vertical separators — ratio-based for dynamic resizing
	table = Table(show_header=False, box=box.SQUARE, expand=True, padding=(0, 1))
	table.add_column(ratio=1)  # 20% izquierda
	table.add_column(ratio=2)  # 40% centro
	table.add_column(ratio=2)  # 40% derecha
	table.add_row(left_window, center_window, right_window)

	# Footer
	footer_parts = [Text("↑/↓ mover · → entrar · ← volver · Esc salir", style="dim")]
	if state.error_message:
		footer_parts.append(Text(state.error_message, style="bold red"))
	footer = Text("\n").join(footer_parts)

	# Layout guarantees header and footer are always visible
	layout = Layout(size=height)
	layout.split_column(
		Layout(name="header", size=1),
		Layout(name="body"),
		Layout(name="footer", size=footer_size),
	)
	layout["header"].update(header)
	layout["body"].update(table)
	layout["footer"].update(footer)

	active_console.print(layout)


def _get_selected_entry(state: AppState) -> FileEntry | None:
	if 0 <= state.selected_index < len(state.current_contents):
		return state.current_contents[state.selected_index]
	return None


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
			raw_lines = file_obj.read().splitlines()
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
		# Size only for directories
		size_label = _format_size(entry) if entry.is_dir else ""
		is_selected = (selected_index is not None and index == selected_index)
		is_highlighted = (current_dir_name and entry.is_dir and entry.name == current_dir_name)

		if no_color:
			prefix = "[DIR] " if entry.is_dir else ""
			if is_selected or is_highlighted:
				prefix = "> " + prefix
			label = f"{prefix}{entry.name}"
			if size_label:
				label += f" {size_label}"
			line = Text(label)
		else:
			name_style = "bold blue" if entry.is_dir else ""
			if is_selected or is_highlighted:
				name_style = "reverse"
			line = Text(entry.name, style=name_style)
			if size_label:
				line.append(f" {size_label}", style="grey70")

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
			# Size only for directories, in light gray
			size_label = _format_size(entry) if entry.is_dir else ""
			if no_color:
				prefix = "[DIR] " if entry.is_dir else ""
				label = f"{prefix}{entry.name}"
				if size_label:
					label += f" {size_label}"
				text = Text(label)
			else:
				text = Text(entry.name, style="bold blue" if entry.is_dir else "")
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
	if not lines:
		return Text("")

	if len(lines) <= visible_height:
		return Text("\n").join(lines)

	start = 0
	if selected_index is not None and selected_index >= 0:
		if selected_index >= visible_height:
			start = selected_index - visible_height + 1
		max_start = max(0, len(lines) - visible_height)
		start = min(start, max_start)

	end = min(len(lines), start + visible_height)
	window = lines[start:end]

	if start > 0:
		window[0] = Text("▲ ") + window[0]
	if end < len(lines):
		window[-1] = Text("▼ ") + window[-1]

	return Text("\n").join(window)
