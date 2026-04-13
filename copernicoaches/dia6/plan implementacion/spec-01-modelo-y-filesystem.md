# Paso 1 — Modelo de estado y capa de sistema de archivos

## Objetivo

Implementar las dos capas fundacionales: el **modelo de estado** (única fuente de verdad) y la **capa de sistema de archivos** (lectura de directorios, metadatos y clasificación de archivos). Estas capas no dependen de visualización ni de navegación.

---

## 1. Modelo de estado (`state/model.py`)

### 1.1 Clase `FileEntry`

Representa un elemento del sistema de archivos visible en las columnas.

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class FileEntry:
    """Elemento del sistema de archivos (archivo o directorio)."""
    name: str
    path: Path
    is_dir: bool
```

### 1.2 Clase `AppState`

Estado completo de la aplicación en todo momento.

```python
@dataclass
class AppState:
    """Estado de la aplicación — única fuente de verdad."""
@dataclass
class AppState:
    """Estado de la aplicación — única fuente de verdad."""
    current_dir: Path
    parent_dir: Path | None
    current_contents: list[FileEntry]
    selected_index: int
    error_message: str | None = None
    is_at_drives: bool = False  # True si estamos en el nivel de unidades
```

### Decisiones de diseño

| Decisión | Justificación |
|----------|---------------|
| `FileEntry` es `frozen` | Inmutable: value object sin identidad propia |
| `AppState` es mutable | El estado se actualiza en cada acción del usuario |
| `selected_index` es un entero | Índice sobre `current_contents`; -1 o manejo especial si vacío |
| `error_message` opcional | Para la barra de estado de errores (CA17) |
| `is_at_drives` booleano | Indica si estamos en el nivel de unidades (nuevo en iteración 2) |

---

## 2. Capa de sistema de archivos (`filesystem/reader.py`)

### 2.1 Función `list_directory(path) -> list[FileEntry]`

Lee el contenido de un directorio y devuelve la lista ordenada de entradas visibles.

**Reglas:**
- Excluir archivos ocultos (dotfiles en Linux/macOS, atributo `hidden` en Windows).
- Excluir enlaces simbólicos.
- Ordenar: directorios primero, luego archivos. Dentro de cada grupo, orden alfabético case-insensitive.
- Manejar errores de acceso (permisos) devolviendo lista vacía + mensaje de error.

```python
def list_directory(path: Path) -> list[FileEntry]:
    """Lista el contenido de un directorio, filtrado y ordenado."""
    ...
```

### 2.2 Función `is_hidden(path) -> bool`

Detecta si un archivo es oculto según el sistema operativo.

- **Linux/macOS:** nombre empieza por `.`
- **Windows:** atributo `FILE_ATTRIBUTE_HIDDEN` vía `ctypes` o `stat`

### 2.3 Función `read_preview(path) -> list[str]`

Genera la vista previa para la columna derecha.

| Tipo | Comportamiento |
|------|----------------|
| Directorio | Devolver lista de nombres de hijos (vía `list_directory`) |
| Archivo de texto (por extensión) | Devolver las primeras 5 líneas (UTF-8) |
| Archivo binario | Devolver solo el nombre del archivo |
| Error de lectura | Devolver mensaje de error |

### 2.4 Extensiones de texto reconocidas

```python
TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".json", ".csv", ".xml", ".html", ".css",
    ".js", ".ts", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".log", ".sh", ".bat", ".ps1", ".sql", ".java", ".c", ".cpp",
    ".h", ".rs", ".go", ".rb", ".php",
}
```

### 2.5 Función `get_parent(path) -> Path | None`

Devuelve el directorio padre, o `None` si es raíz del sistema.

### 2.6 Función `detect_changes(path, known_contents) -> bool`

Compara el contenido actual de un directorio con el conocido para detectar cambios externos.

### 2.7 Función `list_drives() -> list[FileEntry]` (Nuevo en iteración 2)

Obtiene las unidades de disco disponibles.

- **Windows:** Devuelve lista de unidades (C:, D:, E:, etc.) como FileEntry
- **Linux/macOS:** Devuelve solo "/" como FileEntry

Usado para navegar al nivel de unidades de disco inicial.

---

## 3. Tests de este paso

### Tests del modelo

| Test | Verificación |
|------|-------------|
| `test_file_entry_creation` | Crear `FileEntry` con nombre, path y tipo |
| `test_file_entry_immutable` | No se puede modificar un `FileEntry` creado |
| `test_app_state_defaults` | `AppState` se crea con valores por defecto correctos |

### Tests del filesystem

| Test | Verificación |
|------|-------------|
| `test_list_directory_sorts_dirs_first` | Directorios aparecen antes que archivos |
| `test_list_directory_alphabetical` | Orden alfabético case-insensitive dentro de cada grupo |
| `test_list_directory_excludes_hidden` | Archivos ocultos no aparecen |
| `test_list_directory_excludes_symlinks` | Enlaces simbólicos no aparecen |
| `test_list_directory_empty` | Directorio vacío devuelve lista vacía |
| `test_list_directory_permission_error` | Error de permisos devuelve lista vacía |
| `test_read_preview_directory` | Preview de directorio devuelve sus hijos |
| `test_read_preview_text_file` | Preview de archivo `.py` devuelve 5 líneas |
| `test_read_preview_binary_file` | Preview de `.exe` devuelve solo el nombre |
| `test_read_preview_utf8_error` | Error de encoding trata como binario |
| `test_is_hidden_dotfile` | Archivo con `.` inicial es oculto |
| `test_get_parent_root` | Raíz devuelve `None` |
| `test_get_parent_subdir` | Subdirectorio devuelve su padre |

---

## 4. Criterios de validación de este paso

| # | Verificación |
|---|-------------|
| V1 | `AppState` y `FileEntry` se instancian correctamente |
| V2 | `list_directory` devuelve contenido ordenado (dirs primero, alfabético) |
| V3 | Archivos ocultos y symlinks se excluyen |
| V4 | `read_preview` devuelve las 5 primeras líneas para archivos de texto |
| V5 | `read_preview` devuelve solo el nombre para archivos binarios |
| V6 | Errores de acceso se manejan sin crash |
| V7 | Todos los tests pasan |

---

## Trazabilidad

| Criterio de aceptación | Cubierto por |
|------------------------|-------------|
| CA10 (orden) | `list_directory` |
| CA11 (ocultos) | `is_hidden` + filtro en `list_directory` |
| CA12 (symlinks) | Filtro en `list_directory` |
| CA15 (preview texto) | `read_preview` |
| CA16 (preview binario) | `read_preview` |
| CA17 (errores) | Manejo de excepciones en `list_directory` |
| CA19 (vacío) | `list_directory` con directorio vacío |

---

## ✅ Estado de implementación (23–27 de marzo de 2026)

**Completado exitosamente**

- ✅ `FileEntry` implementado como dataclass frozen (value object)
- ✅ `AppState` implementado como dataclass mutable (estado único)
- ✅ `list_directory()` completo: filtrado (ocultos, symlinks), ordenamiento (dirs primero, alfabético case-insensitive)
- ✅ `is_hidden()` con soporte multiplataforma (Windows FILE_ATTRIBUTE_HIDDEN, Unix dotfiles)
- ✅ `read_preview()` con detección de tipo por extensión y lectura UTF-8
- ✅ `get_parent()` y `detect_changes()` implementados
- ✅ **18 tests pasados** (test_model.py: 6, test_reader.py: 18)
- ✅ Manejo de errores de permisos sin crash de la aplicación
- ✅ Sincronización con OpenSpec completada (27 de marzo)

**Cobertura de criterios de aceptación:** CA10, CA11, CA12, CA15, CA16, CA17, CA19
