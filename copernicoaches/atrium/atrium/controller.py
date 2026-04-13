from __future__ import annotations

from pathlib import Path

from .display import DisplayColumn, DisplayRow, DisplayState
from .filesystem import DirectoryListing, FileInfo, FilesystemAdapter
from .state import AtriumState, build_initial_state


class NavigationController:
    """Mutates navigation state in response to user intent."""

    def __init__(
        self,
        *,
        start_path: Path | None = None,
        filesystem: FilesystemAdapter | None = None,
    ) -> None:
        self.filesystem = filesystem or FilesystemAdapter()
        self.state = build_initial_state(start_path, filesystem=self.filesystem)

    def move_up(self) -> None:
        self._move_selection(-1)

    def move_down(self) -> None:
        self._move_selection(1)

    def enter_selection(self) -> bool:
        selected = self.state.selected
        if selected is None or not selected.is_dir:
            return False

        self._load_directory(selected.path)
        return True

    def go_parent(self) -> bool:
        if self.state.parent_dir is None:
            return False

        old_current_dir = self.state.current_dir
        self._load_directory(self.state.parent_dir)
        restored = next(
            (entry for entry in self.state.current_entries if entry.path == old_current_dir),
            None,
        )
        self.state.selected = restored
        self.state.preview_target = restored
        return True

    def _move_selection(self, offset: int) -> None:
        if not self.state.current_entries or self.state.selected is None:
            return

        current_index = self.state.current_entries.index(self.state.selected)
        new_index = max(0, min(len(self.state.current_entries) - 1, current_index + offset))
        selected = self.state.current_entries[new_index]
        self.state.selected = selected
        self.state.preview_target = selected

    def _load_directory(self, path: Path) -> None:
        listing = self.filesystem.list_directory(path)
        current_dir = listing.path
        selected = listing.entries[0] if listing.entries else None

        self.state.current_dir = current_dir
        self.state.parent_dir = current_dir.parent if current_dir.parent != current_dir else None
        self.state.current_entries = listing.entries
        self.state.selected = selected
        self.state.preview_target = selected
        self.state.current_error = listing.error

    def build_display_state(self, *, column_width: int = 32, viewport_height: int = 1) -> DisplayState:
        parent_listing = self._parent_listing()
        left_rows = self._directory_rows(
            parent_listing,
            highlight_path=self.state.current_dir,
            empty_text="Root",
        )
        center_rows = self._directory_rows(
            DirectoryListing(
                path=self.state.current_dir,
                entries=self.state.current_entries,
                error=self.state.current_error,
            ),
            highlight_path=self.state.selected.path if self.state.selected else None,
            empty_text="Empty directory",
        )
        preview_rows = self._preview_rows()
        return DisplayState(
            current_path=str(self.state.current_dir),
            column_width=column_width,
            left=DisplayColumn(
                title="Parent",
                rows=left_rows,
                selected_index=_selected_index(left_rows),
            ),
            center=DisplayColumn(
                title="Current",
                rows=center_rows,
                emphasized=True,
                selected_index=_selected_index(center_rows),
            ),
            right=DisplayColumn(
                title="Preview",
                rows=preview_rows,
                selected_index=_selected_index(preview_rows),
            ),
        )

    def _parent_listing(self) -> DirectoryListing | None:
        if self.state.parent_dir is None:
            return None
        return self.filesystem.list_directory(self.state.parent_dir)

    def _directory_rows(
        self,
        listing: DirectoryListing | None,
        *,
        highlight_path: Path | None,
        empty_text: str,
    ) -> tuple[DisplayRow, ...]:
        if listing is None:
            return (DisplayRow(text=empty_text, kind="empty"),)
        if listing.error:
            return (DisplayRow(text=listing.error, kind="error"),)
        if not listing.entries:
            return (DisplayRow(text=empty_text, kind="empty"),)
        return tuple(
            DisplayRow(
                text=entry.name,
                kind="directory" if entry.is_dir else "file",
                highlighted=entry.path == highlight_path,
            )
            for entry in listing.entries
        )

    def _preview_rows(self) -> tuple[DisplayRow, ...]:
        target = self.state.preview_target
        if target is None:
            return ()
        if target.is_dir:
            listing = self.filesystem.list_directory(target.path)
            return self._directory_rows(listing, highlight_path=None, empty_text="Empty directory")

        info = self.filesystem.describe_file(target.path)
        return self._file_rows(info)

    def _file_rows(self, info: FileInfo) -> tuple[DisplayRow, ...]:
        rows = [
            DisplayRow(text=f"Name: {info.name}", kind="info"),
            DisplayRow(text=f"Type: {info.file_type}", kind="info"),
            DisplayRow(text=f"Size: {info.size} B", kind="info"),
        ]
        if info.error:
            rows.append(DisplayRow(text=info.error, kind="error"))
            return tuple(rows)
        rows.extend(DisplayRow(text=line, kind="info") for line in info.excerpt)
        return tuple(rows)


def _selected_index(rows: tuple[DisplayRow, ...]) -> int | None:
    for index, row in enumerate(rows):
        if row.highlighted:
            return index
    return None
