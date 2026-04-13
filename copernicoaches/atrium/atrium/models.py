from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Entry:
    name: str
    path: Path
    is_dir: bool

    @classmethod
    def from_path(cls, path: Path) -> Entry:
        resolved = path.resolve()
        return cls(name=resolved.name, path=resolved, is_dir=resolved.is_dir())
