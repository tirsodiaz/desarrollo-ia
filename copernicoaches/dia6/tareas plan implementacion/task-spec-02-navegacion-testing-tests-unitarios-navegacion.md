# SPEC-02 | NAVEGACION | TESTING | Tests unitarios: Navigator e input handler

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-02-navegacion-testing-tests-unitarios-navegacion |
| **CÃ³digo de plan** | SPEC-02 |
| **Ã‰pica** | NAVEGACION â€” LÃ³gica de navegaciÃ³n |
| **Feature** | TESTING â€” Suite de tests unitarios de Capa 2 |
| **Tipo** | Tarea tÃ©cnica â€” Testing |
| **Prioridad** | Alta |
| **EstimaciÃ³n** | 4 h |

---

## DescripciÃ³n tÃ©cnica

Implementar los tests unitarios para la capa de navegaciÃ³n. Los tests usan un **fake reader** que aisla completamente el `Navigator` del disco real. Cobertura mÃ­nima esperada: **85%** para `navigation/navigator.py`.

### Fake reader compartido (`tests/conftest.py`)

```python
class FakeReader:
    def list_directory(self, path): return FIXTURE_CONTENTS.get(path, [])
    def list_drives(self): return [FileEntry("C:", Path("C:\\"), True)]
    def detect_changes(self, path, known): return False
    def get_parent(self, path): return path.parent if path.parent != path else None
```

### Tests del Navigator (`tests/test_navigator.py`)

| ID | Nombre | VerificaciÃ³n |
|----|--------|-------------|
| TN-01 | `test_initialize_root` | `is_at_drives=True`, `parent_dir=None`, `selected_index=0` |
| TN-02 | `test_move_up_decrements` | `selected_index` baja de 2 a 1 |
| TN-03 | `test_move_up_at_top_stays` | `selected_index=0` no cambia |
| TN-04 | `test_move_down_increments` | `selected_index` sube de 0 a 1 |
| TN-05 | `test_move_down_at_bottom_stays` | En el Ãºltimo elemento, Ã­ndice no cambia |
| TN-06 | `test_move_empty_directory` | `selected_index=-1`: arriba/abajo sin efecto |
| TN-07 | `test_enter_directory` | Entrar en dir actualiza `current_dir`, `current_contents`, `selected_index=0` |
| TN-08 | `test_enter_file_no_effect` | Flecha derecha sobre archivo (`is_dir=False`) â†’ estado idÃ©ntico |
| TN-09 | `test_go_parent` | `current_dir` pasa a ser el `parent_dir` anterior |
| TN-10 | `test_go_parent_selects_previous` | `selected_index` apunta al directorio de origen |
| TN-11 | `test_go_parent_at_root` | `is_at_drives=True` â†’ `go_parent` no cambia estado |
| TN-12 | `test_enter_empty_directory` | Directorio vacÃ­o â†’ `selected_index=-1` |
| TN-13 | `test_enter_permission_error` | `PermissionError` â†’ `error_message` â‰  None, `current_dir` sin cambio |
| TN-14 | `test_refresh_detects_new_file` | Nuevo archivo en mock â†’ `current_contents` actualizado |
| TN-15 | `test_refresh_deleted_selection` | Elemento borrado â†’ `selected_index` ajustado a `len-1` |
| TN-16 | `test_navigation_clears_error` | Navegar tras error limpia `error_message` a `None` |

### Tests del input handler (`tests/test_input_handler.py`)

| ID | Nombre | VerificaciÃ³n |
|----|--------|-------------|
| TI-01 | `test_arrow_keys_mapping` | Mock de `msvcrt.getwch` / `sys.stdin.read` â†’ cada secuencia produce el string esperado |

---

## Objetivo arquitectÃ³nico

Cerrar el ciclo de confianza en la **Capa 2** antes de integrarla con la visualizaciÃ³n. La navegaciÃ³n es el corazÃ³n de la aplicaciÃ³n; la calidad de estos tests determina la estabilidad del sistema completo.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | Los 16 tests del Navigator pasan |
| CA-2 | El test de input handler pasa en la plataforma de desarrollo |
| CA-3 | Los tests de navegaciÃ³n no acceden al disco |
| CA-4 | Cobertura de `navigation/navigator.py` â‰¥ 85% |
| CA-5 | Suite SPEC-02 completa en < 10 segundos |

---

## Artefactos y entregables

- `tests/test_navigator.py` con 16 tests
- `tests/test_input_handler.py` con 1 test
- `tests/conftest.py` con `FakeReader` y fixtures compartidos

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-02-NAVEGACION-NAVIGATOR (implementado) |
| **Interna** | SPEC-02-NAVEGACION-INPUT (implementado) |
| **Bloquea** | PR de SPEC-02 no puede cerrarse sin todos los tests pasando |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| TN-10 difÃ­cil de aislar si `go_parent` usa lÃ³gica compleja de Ã­ndice | DiseÃ±ar fixture con contenido predecible y conocer el Ã­ndice esperado de antemano |
| TI-01 no ejecutable en CI headless | `unittest.mock.patch` para `msvcrt` / `termios` |


