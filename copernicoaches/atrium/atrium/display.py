from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from typing import Literal

from rich.cells import cell_len, chop_cells, set_cell_size


RowKind = Literal["directory", "empty", "error", "file", "info"]

VERTICAL_SEPARATOR = "│"
HORIZONTAL_SEPARATOR = "─"
ELLIPSIS = "…"
SELECTION_MARKER = "▶"
ROW_ICONS = {
    "directory": "📁",
    "file": "📄",
}


@dataclass(frozen=True, slots=True)
class DisplayRow:
    text: str
    kind: RowKind
    highlighted: bool = False


@dataclass(frozen=True, slots=True)
class DisplayColumn:
    title: str
    rows: tuple[DisplayRow, ...]
    emphasized: bool = False
    selected_index: int | None = None


@dataclass(frozen=True, slots=True)
class DisplayState:
    current_path: str
    column_width: int
    left: DisplayColumn
    center: DisplayColumn
    right: DisplayColumn


def render_display(state: DisplayState, *, viewport_height: int) -> str:
    """Render a full textual projection with aligned fixed-width columns."""

    width = state.column_width
    columns = (state.left, state.center, state.right)
    viewport_height = max(1, viewport_height)
    header = f"Path: {state.current_path}"
    title_row = _framed_row(_fit(_title_text(column), width) for column in columns)
    separator_row = _separator_row(width, len(columns))
    body_rows = []
    visible_columns = tuple(
        _visible_rows(column, viewport_height=viewport_height, scroll_offset=0) for column in columns
    )

    for index in range(viewport_height):
        parts = []
        for rows in visible_columns:
            row = rows[index]
            parts.append(_fit(_row_text(row), width))
        body_rows.append(_framed_row(parts))

    return "\n".join([header, "", title_row, separator_row, *body_rows])


class DisplayRenderer:
    """Pure renderer for display state."""

    def __init__(self) -> None:
        self._center_scroll_offset = 0

    def reset_center_scroll(self) -> None:
        self._center_scroll_offset = 0

    def render(self, state: DisplayState, *, viewport_height: int) -> str:
        viewport_height = max(1, viewport_height)
        width = state.column_width
        columns = (state.left, state.center, state.right)
        header = f"Path: {state.current_path}"
        title_row = _framed_row(_fit(_title_text(column), width) for column in columns)
        separator_row = _separator_row(width, len(columns))
        left_rows = _visible_rows(state.left, viewport_height=viewport_height, scroll_offset=0)
        center_rows, self._center_scroll_offset = _visible_rows(
            state.center,
            viewport_height=viewport_height,
            scroll_offset=self._center_scroll_offset,
            return_scroll_offset=True,
        )
        right_rows = _visible_rows(state.right, viewport_height=viewport_height, scroll_offset=0)
        body_rows = [
            _framed_row(
                _fit(_row_text(row), width)
                for row in (left_rows[index], center_rows[index], right_rows[index])
            )
            for index in range(viewport_height)
        ]
        return "\n".join([header, "", title_row, separator_row, *body_rows])


def _title_text(column: DisplayColumn) -> str:
    if column.emphasized:
        return f"[* {column.title} *]"
    return column.title


def _row_text(row: DisplayRow | None) -> str:
    if row is None:
        return ""

    marker = SELECTION_MARKER if row.highlighted else " "
    icon = ROW_ICONS.get(row.kind)
    content = f"{icon} {row.text}" if icon else row.text
    return f"{marker} {content}"


def _fit(text: str, width: int) -> str:
    if cell_len(text) > width:
        if width <= 1:
            return ELLIPSIS[:width]
        text = f"{chop_cells(text, width - 1)[0]}{ELLIPSIS}"
    return set_cell_size(text, width)


def _framed_row(parts: Iterable[str]) -> str:
    return f"{VERTICAL_SEPARATOR} {' │ '.join(parts)} {VERTICAL_SEPARATOR}"


def _separator_row(width: int, column_count: int) -> str:
    segment = HORIZONTAL_SEPARATOR * (width + 2)
    return VERTICAL_SEPARATOR + VERTICAL_SEPARATOR.join(segment for _ in range(column_count)) + VERTICAL_SEPARATOR


def _visible_rows(
    column: DisplayColumn,
    *,
    viewport_height: int,
    scroll_offset: int,
    return_scroll_offset: bool = False,
) -> tuple[DisplayRow | None, ...] | tuple[tuple[DisplayRow | None, ...], int]:
    viewport_height = max(1, viewport_height)
    scroll_offset = _resolve_scroll_offset(
        item_count=len(column.rows),
        selected_index=column.selected_index,
        scroll_offset=scroll_offset,
        viewport_height=viewport_height,
    )
    rows = tuple(
        column.rows[index] if index < len(column.rows) else None
        for index in range(scroll_offset, scroll_offset + viewport_height)
    )
    if return_scroll_offset:
        return rows, scroll_offset
    return rows


def _resolve_scroll_offset(
    *,
    item_count: int,
    selected_index: int | None,
    scroll_offset: int,
    viewport_height: int,
) -> int:
    viewport_height = max(1, viewport_height)
    max_offset = max(0, item_count - viewport_height)
    scroll_offset = max(0, min(scroll_offset, max_offset))

    if selected_index is not None:
        if selected_index < scroll_offset:
            scroll_offset = selected_index
        if selected_index >= scroll_offset + viewport_height:
            scroll_offset = selected_index - viewport_height + 1

    return max(0, min(scroll_offset, max_offset))
