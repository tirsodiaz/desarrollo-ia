from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .filesystem import FilesystemAdapter
from .models import Entry


@dataclass(slots=True)
class AtriumState:
    current_dir: Path
    parent_dir: Path | None
    current_entries: tuple[Entry, ...]
    selected: Entry | None
    preview_target: Entry | None
    current_error: str | None = None


def build_initial_state(
    start_path: Path | None = None,
    *,
    filesystem: FilesystemAdapter | None = None,
) -> AtriumState:
    adapter = filesystem or FilesystemAdapter()
    current_dir = (start_path or Path.cwd()).resolve()
    listing = adapter.list_directory(current_dir)
    selected = listing.entries[0] if listing.entries else None

    return AtriumState(
        current_dir=current_dir,
        parent_dir=current_dir.parent if current_dir.parent != current_dir else None,
        current_entries=listing.entries,
        selected=selected,
        preview_target=selected,
        current_error=listing.error,
    )
