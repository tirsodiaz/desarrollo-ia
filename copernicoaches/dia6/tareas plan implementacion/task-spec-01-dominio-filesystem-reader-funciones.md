# SPEC-01 | DOMINIO | FILESYSTEM | Implementar capa de sistema de archivos (reader.py)

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-01-dominio-filesystem-reader-funciones |
| **CÃ³digo de plan** | SPEC-01 |
| **Ã‰pica** | DOMINIO â€” Modelo de estado y capa de sistema de archivos |
| **Feature** | FILESYSTEM â€” Capa de acceso al sistema de archivos (Capa 3) |
| **Tipo** | Tarea tÃ©cnica â€” Capa de infraestructura |
| **Prioridad** | CrÃ­tica |
| **EstimaciÃ³n** | 4 h |

---

## DescripciÃ³n tÃ©cnica

Implementar todas las funciones pÃºblicas de `filesystem/reader.py`. Este mÃ³dulo es el Ãºnico punto de acceso al sistema de archivos real; actÃºa como **anti-corruption layer** entre el SO y el dominio.

### Funciones a implementar

| FunciÃ³n | Responsabilidad |
|---------|----------------|
| `list_directory(path) -> list[FileEntry]` | Lee, filtra (ocultos, symlinks) y ordena (dirs primero, alfabÃ©tico) el contenido de un directorio |
| `is_hidden(path) -> bool` | DetecciÃ³n multiplataforma: dotfile en Unix, `FILE_ATTRIBUTE_HIDDEN` en Windows |
| `read_preview(path) -> list[str]` | Preview: hijos si es dir; primeras 5 lÃ­neas si texto; nombre si binario |
| `get_parent(path) -> Path \| None` | Padre del path; `None` si es raÃ­z del sistema |
| `detect_changes(path, known) -> bool` | Compara contenido actual con `known_contents`; `True` si hay diferencias |
| `list_drives() -> list[FileEntry]` | Unidades activas en Windows (C:, D:â€¦); `["/"]` en Unix |

### Constante `TEXT_EXTENSIONS`

```python
TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".json", ".csv", ".xml", ".html", ".css",
    ".js", ".ts", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".log", ".sh", ".bat", ".ps1", ".sql", ".java", ".c", ".cpp",
    ".h", ".rs", ".go", ".rb", ".php",
}
```

### Reglas de `list_directory`

- Excluir archivos ocultos (`is_hidden`).
- Excluir enlaces simbÃ³licos (`path.is_symlink()`).
- Ordenar: directorios primero, luego archivos; cada grupo en orden alfabÃ©tico case-insensitive.
- Ante `PermissionError` / `OSError`: devolver lista vacÃ­a sin propagar la excepciÃ³n.

---

## Objetivo arquitectÃ³nico

Implementar la **Capa 3 (Filesystem)** como mÃ³dulo de infraestructura puro. Al encapsular todas las diferencias de SO (ocultos, unidades de disco, permisos), las capas superiores son completamente portables y testeables con mocks.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | `list_directory` devuelve dirs antes que archivos, ambos grupos en alfabÃ©tico case-insensitive |
| CA-2 | `list_directory` excluye dotfiles (Unix) y archivos con atributo `hidden` (Windows) |
| CA-3 | `list_directory` excluye symlinks |
| CA-4 | `list_directory` retorna lista vacÃ­a ante `PermissionError` sin lanzar excepciÃ³n |
| CA-5 | `read_preview` devuelve exactamente las primeras 5 lÃ­neas para archivos de texto |
| CA-6 | `read_preview` devuelve solo el nombre para archivos binarios |
| CA-7 | `get_parent` devuelve `None` para rutas raÃ­z del sistema |
| CA-8 | `detect_changes` detecta creaciones y eliminaciones de archivos |
| CA-9 | `list_drives` funciona en Windows y Linux/macOS sin error |
| CA-10 | El mÃ³dulo no importa de `navigation`, `ui` ni `state` |

---

## Artefactos y entregables

- `src/miller/filesystem/reader.py`
- `tests/test_reader.py` con tests unitarios (ver SPEC-01-DOMINIO-TESTING)

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-01-DOMINIO-MODELO (`FileEntry` definido) |
| **Bloquea** | SPEC-02-NAVEGACION-NAVIGATOR (`Navigator` inyecta este mÃ³dulo) |
| **Bloquea** | SPEC-01-DOMINIO-TESTING |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| DetecciÃ³n de ocultos difiere entre SO | Rama `sys.platform == "win32"` con `ctypes`; fallback a dotfile |
| Archivos con encoding no UTF-8 | Capturar `UnicodeDecodeError` y tratar como binario |
| Directorios de red con latencia alta | Documentar como limitaciÃ³n conocida del MVP |


