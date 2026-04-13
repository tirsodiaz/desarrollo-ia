from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import Entry


@dataclass(frozen=True, slots=True)
class DirectoryListing:
    path: Path
    entries: tuple[Entry, ...]
    error: str | None = None


@dataclass(frozen=True, slots=True)
class FileInfo:
    name: str
    file_type: str
    size: int
    excerpt: tuple[str, ...]
    error: str | None = None


class FilesystemAdapter:
    """Filesystem access with no knowledge of navigation or display."""

    def list_directory(self, path: Path) -> DirectoryListing:
        resolved = path.resolve()
        try:
            children = sorted(
                resolved.iterdir(),
                key=lambda child: (not child.is_dir(), child.name.casefold()),
            )
        except PermissionError:
            return DirectoryListing(path=resolved, entries=(), error="Permission denied")

        entries = tuple(Entry.from_path(child) for child in children)
        return DirectoryListing(path=resolved, entries=entries)

    def describe_file(self, path: Path, *, max_lines: int = 5, max_bytes: int = 4096) -> FileInfo:
        resolved = path.resolve()
        stat = resolved.stat()
        file_type = resolved.suffix.lstrip(".") or "file"

        try:
            sample = resolved.read_bytes()[:max_bytes]
        except PermissionError:
            return FileInfo(
                name=resolved.name,
                file_type=file_type,
                size=stat.st_size,
                excerpt=(),
                error="Permission denied",
            )

        excerpt = ()
        if b"\x00" not in sample:
            try:
                text = sample.decode("utf-8")
            except UnicodeDecodeError:
                text = ""
            if text:
                excerpt = tuple(text.splitlines()[:max_lines])

        return FileInfo(
            name=resolved.name,
            file_type=file_type,
            size=stat.st_size,
            excerpt=excerpt,
        )
