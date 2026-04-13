"""Modelo de estado — única fuente de verdad de la aplicación."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FileEntry:
    """Elemento del sistema de archivos (archivo o directorio)."""

    name: str
    path: Path
    is_dir: bool
    size_bytes: int | None = None


@dataclass
class AppState:
    """Estado de la aplicación — única fuente de verdad."""

    current_dir: Path
    parent_dir: Path | None
    current_contents: list[FileEntry] = field(default_factory=list)
    selected_index: int = -1
    error_message: str | None = None
    is_at_drives: bool = False  # True si estamos en el nivel de unidades de disco
