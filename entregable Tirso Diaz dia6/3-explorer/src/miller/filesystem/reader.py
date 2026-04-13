"""Capa de sistema de archivos — lectura de directorios, metadatos y clasificación."""

import os
import platform
import sys
from pathlib import Path

from miller.state.model import FileEntry

TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".json", ".csv", ".xml", ".html", ".css",
    ".js", ".ts", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".log", ".sh", ".bat", ".ps1", ".sql", ".java", ".c", ".cpp",
    ".h", ".rs", ".go", ".rb", ".php",
}


def is_hidden(path: Path) -> bool:
    """Detecta si un archivo/directorio es oculto según el SO."""
    if path.name.startswith("."):
        return True
    if sys.platform == "win32":
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            if attrs == -1:
                return False
            FILE_ATTRIBUTE_HIDDEN = 0x2
            return bool(attrs & FILE_ATTRIBUTE_HIDDEN)
        except (AttributeError, OSError):
            return False
    return False


def list_directory(path: Path) -> list[FileEntry]:
    """Lista el contenido de un directorio, filtrado y ordenado.

    Reglas:
    - Excluir archivos ocultos y enlaces simbólicos.
    - Directorios primero, luego archivos.
    - Orden alfabético case-insensitive dentro de cada grupo.
    """
    try:
        entries = list(path.iterdir())
    except PermissionError:
        return []
    except OSError:
        return []

    result: list[FileEntry] = []
    for entry in entries:
        if entry.is_symlink():
            continue
        if is_hidden(entry):
            continue
        try:
            is_dir = entry.is_dir()
            size_bytes = entry.stat().st_size
        except OSError:
            continue
        result.append(FileEntry(name=entry.name, path=entry, is_dir=is_dir, size_bytes=size_bytes))

    result.sort(key=lambda e: (not e.is_dir, e.name.lower()))
    return result


def read_preview(path: Path) -> list[str]:
    """Genera la vista previa para la columna derecha.

    - Directorio: lista de nombres de hijos.
    - Archivo de texto (por extensión): primeras 5 líneas UTF-8.
    - Archivo binario: solo el nombre.
    - Error de lectura: mensaje de error.
    """
    try:
        if path.is_dir():
            children = list_directory(path)
            return [c.name for c in children]

        if path.suffix.lower() in TEXT_EXTENSIONS:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= 5:
                            break
                        lines.append(line.rstrip("\n\r"))
                    return lines
            except (UnicodeDecodeError, ValueError):
                return [path.name]

        return [path.name]
    except PermissionError:
        return ["Error: acceso denegado"]
    except OSError as e:
        return [f"Error: {e}"]


def get_parent(path: Path) -> Path | None:
    """Devuelve el directorio padre, o None si es raíz del sistema."""
    parent = path.parent
    if parent == path:
        return None
    return parent


def detect_changes(path: Path, known_contents: list[FileEntry]) -> bool:
    """Compara el contenido actual con el conocido para detectar cambios externos."""
    try:
        current = list_directory(path)
    except OSError:
        return True

    if len(current) != len(known_contents):
        return True

    for cur, known in zip(current, known_contents):
        if cur.name != known.name or cur.is_dir != known.is_dir:
            return True

    return False


def list_drives() -> list[FileEntry]:
    """Lista las unidades de disco disponibles.

    - Windows: C:, D:, E:, etc. (sólo las que existen)
    - Unix/Linux/macOS: devuelve sólo "/" (raíz)
    """
    if sys.platform == "win32":
        import ctypes
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1 << i):
                drive_letter = chr(65 + i)  # A, B, C, ...
                drive_path = Path(f"{drive_letter}:\\")
                # Crear un FileEntry representando la unidad
                drives.append(FileEntry(
                    name=f"{drive_letter}:",
                    path=drive_path,
                    is_dir=True,
                    size_bytes=None,
                ))
        return sorted(drives, key=lambda e: e.name)
    else:
        # En Unix: solo la raíz
        return [FileEntry(name="/", path=Path("/"), is_dir=True, size_bytes=None)]
