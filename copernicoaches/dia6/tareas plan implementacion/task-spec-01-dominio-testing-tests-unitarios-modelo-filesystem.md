# SPEC-01 | DOMINIO | TESTING | Tests unitarios: modelo de estado y filesystem

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-01-dominio-testing-tests-unitarios-modelo-filesystem |
| **CÃ³digo de plan** | SPEC-01 |
| **Ã‰pica** | DOMINIO â€” Modelo de estado y capa de sistema de archivos |
| **Feature** | TESTING â€” Suite de tests unitarios de Capa 1 y Capa 3 |
| **Tipo** | Tarea tÃ©cnica â€” Testing |
| **Prioridad** | Alta |
| **EstimaciÃ³n** | 3 h |

---

## DescripciÃ³n tÃ©cnica

Implementar los tests unitarios que validan el modelo de estado y la capa de filesystem. Los tests usan `tmp_path` de pytest; no acceden nunca al sistema de archivos real fuera de ese directorio temporal. Cobertura mÃ­nima esperada: **90%** para `state/model.py`, **85%** para `filesystem/reader.py`.

### Tests del modelo (`tests/test_model.py`)

| ID | Nombre | VerificaciÃ³n |
|----|--------|-------------|
| TM-01 | `test_file_entry_creation` | `FileEntry` se instancia con `name`, `path` (Path) e `is_dir` correctamente |
| TM-02 | `test_file_entry_immutable` | Asignar `entry.name = "x"` lanza `FrozenInstanceError` |
| TM-03 | `test_app_state_defaults` | `error_message=None` e `is_at_drives=False` por defecto |

### Tests del filesystem (`tests/test_reader.py`)

| ID | Nombre | VerificaciÃ³n |
|----|--------|-------------|
| TF-01 | `test_list_directory_sorts_dirs_first` | Subdirectorios aparecen antes que archivos |
| TF-02 | `test_list_directory_alphabetical` | Orden alphabÃ©tico case-insensitive dentro de cada grupo |
| TF-03 | `test_list_directory_excludes_hidden` | Archivo `.hidden` no aparece en resultado |
| TF-04 | `test_list_directory_excludes_symlinks` | Enlace simbÃ³lico no aparece |
| TF-05 | `test_list_directory_empty` | Directorio vacÃ­o â†’ lista vacÃ­a sin excepciÃ³n |
| TF-06 | `test_list_directory_permission_error` | Directorio sin permisos â†’ lista vacÃ­a |
| TF-07 | `test_read_preview_directory` | Preview de directorio devuelve nombres de sus hijos |
| TF-08 | `test_read_preview_text_file` | Archivo `.py` con 10 lÃ­neas â†’ exactamente 5 lÃ­neas |
| TF-09 | `test_read_preview_binary_file` | Archivo `.exe` â†’ lista con solo el nombre |
| TF-10 | `test_read_preview_utf8_error` | Bytes invÃ¡lidos UTF-8 â†’ tratado como binario |
| TF-11 | `test_is_hidden_dotfile` | `Path(".bashrc")` es oculto |
| TF-12 | `test_get_parent_root` | RaÃ­z del sistema devuelve `None` |
| TF-13 | `test_get_parent_subdir` | `Path("/tmp/a/b")` devuelve `Path("/tmp/a")` |

### ConfiguraciÃ³n de pytest

```toml
# en pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short"
```

Comando de cobertura: `pytest --cov=miller --cov-report=term-missing`

---

## Objetivo arquitectÃ³nico

Asegurar que las dos capas fundacionales son correctas de forma aislada antes de construir sobre ellas. Los tests actÃºan como **contrato de interfaz**: un cambio en `FileEntry` o en `reader.py` que rompa estos tests es una regresiÃ³n, no una refactorizaciÃ³n.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | Los 3 tests de modelo pasan |
| CA-2 | Los 13 tests de filesystem pasan |
| CA-3 | NingÃºn test accede al filesystem real (solo `tmp_path`) |
| CA-4 | Cobertura de `state/model.py` â‰¥ 90% |
| CA-5 | Cobertura de `filesystem/reader.py` â‰¥ 85% |
| CA-6 | Suite completa termina en < 5 segundos |

---

## Artefactos y entregables

- `tests/test_model.py` â€” 3 tests
- `tests/test_reader.py` â€” 13 tests
- Reporte de cobertura con `pytest-cov`

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-01-DOMINIO-MODELO (implementado) |
| **Interna** | SPEC-01-DOMINIO-FILESYSTEM (implementado) |
| **Bloquea** | PR de SPEC-01 no puede cerrarse sin todos los tests pasando |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| TF-06 (permisos) falla en Windows | `pytest.mark.skipif(sys.platform=="win32", ...)` o mock de `os.listdir` |
| TF-04 (symlinks) requiere privilegios en Windows | `pytest.mark.skipif` cuando no hay permisos de symlink |


