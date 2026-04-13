# SPEC-03 | VISUALIZACION | TESTING | Tests del renderizador

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-03-visualizacion-testing-tests-renderizador |
| **CÃ³digo de plan** | SPEC-03 |
| **Ã‰pica** | VISUALIZACION â€” VisualizaciÃ³n con Rich |
| **Feature** | TESTING â€” Suite de tests del renderizador |
| **Tipo** | Tarea tÃ©cnica â€” Testing |
| **Prioridad** | Alta |
| **EstimaciÃ³n** | 3 h |

---

## DescripciÃ³n tÃ©cnica

Implementar los tests que validan el output visual del renderer. Los tests capturan la salida de Rich en buffer en memoria â€” nunca escriben en pantalla real â€” usando `Console(file=StringIO(), force_terminal=True)`.

### TÃ©cnica de captura

```python
from io import StringIO
from rich.console import Console

def make_test_console(width=80, height=24) -> Console:
    return Console(file=StringIO(), force_terminal=True,
                   force_jupyter=False, width=width, height=height)
```

El renderer debe aceptar un `Console` inyectado (parÃ¡metro o constructor de clase) para que los tests puedan proporcionar su propia instancia.

### Tests (`tests/test_renderer.py`)

| ID | Nombre | VerificaciÃ³n |
|----|--------|-------------|
| TR-01 | `test_render_empty_state` | Estado con `current_contents=[]` no lanza excepciÃ³n; hay output |
| TR-02 | `test_render_with_contents` | 3 entradas â†’ output contiene los 3 nombres |
| TR-03 | `test_truncation` | Nombre de 100 chars en consola de 20 cols â†’ output contiene `â€¦` |
| TR-04 | `test_directory_style` | Output de directorio contiene secuencia ANSI `bold blue` (o `[DIR]` en degradado) |
| TR-05 | `test_selected_highlight` | Output del elemento con `selected_index` contiene secuencia `reverse` |
| TR-06 | `test_error_message_displayed` | `error_message="Sin permisos"` â†’ output contiene ese string |
| TR-07 | `test_scroll_indicators` | 50 entradas, terminal 10 lÃ­neas, `selected_index=25` â†’ output contiene `â–²` y `â–¼` |
| TR-08 | `test_parent_column_at_root` | `is_at_drives=True` â†’ columna izquierda no contiene nombres de archivos |
| TR-09 | `test_parent_column_highlights_current` | NavegaciÃ³n normal â†’ columna izquierda contiene nombre del dir actual con `reverse` |
| TR-10 | `test_header_shows_path` | Output contiene `str(state.current_dir)` |

### Fixture de estado (`tests/conftest.py`)

```python
@pytest.fixture
def sample_state(tmp_path):
    (tmp_path / "alpha").mkdir()
    (tmp_path / "beta.txt").write_text("contenido")
    return AppState(
        current_dir=tmp_path,
        parent_dir=tmp_path.parent,
        current_contents=[
            FileEntry("alpha", tmp_path / "alpha", True),
            FileEntry("beta.txt", tmp_path / "beta.txt", False),
        ],
        selected_index=0,
    )
```

---

## Objetivo arquitectÃ³nico

Los tests del renderer son la red de seguridad de la capa visual: permiten detectar regresiones de estilo o layout sin validaciÃ³n manual. Al ser reproducibles en CI headless, cierran el ciclo de calidad de la capa mÃ¡s expuesta al usuario.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | Los 10 tests pasan (`pytest tests/test_renderer.py`) |
| CA-2 | Los tests no escriben en pantalla real (solo en `StringIO`) |
| CA-3 | Los tests son reproducibles en CI sin display |
| CA-4 | Cobertura de `ui/renderer.py` â‰¥ 80% |
| CA-5 | Cada test verifica exactamente la condiciÃ³n de su nombre |

---

## Artefactos y entregables

- `tests/test_renderer.py` con 10 tests
- `tests/conftest.py` actualizado con `sample_state` y `make_test_console`

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-03-VISUALIZACION-RENDERER (implementado) |
| **Interna** | SPEC-03-VISUALIZACION-SCROLL (implementado) |
| **Bloquea** | PR de SPEC-03 no puede cerrarse sin todos los tests pasando |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| Rich no emite secuencias ANSI en `StringIO` sin flag correcto | Usar `Console(force_terminal=True, force_jupyter=False)` explÃ­citamente |
| TR-04 / TR-05 frÃ¡giles si Rich cambia formato de secuencias entre versiones | Verificar presencia del texto del nombre, no de secuencias raw |
| TR-07: aislar output por columna es difÃ­cil | Buscar `â–¼` / `â–²` en el output completo capturado |

---

## Actualizacion OpenSpec 2026-03-27

### Nuevos tests requeridos

- `test_header_stays_visible_while_scrolling_down`: validar que la ruta activa sigue presente durante desplazamiento descendente.
- `test_header_stays_visible_while_scrolling_up`: validar persistencia de cabecera tras recuperar bloques previos.
- `test_dynamic_block_rendering_down_up`: validar comportamiento por bloques visibles en ambas direcciones.
- `test_selection_counter_is_inline_in_header`: validar que `[n/N]` se muestra en la misma línea de ayuda.
- `test_footer_does_not_render_standalone_counter_line`: validar que no existe línea independiente con solo `[n/N]`.
- `test_navigation_help_text_visible_with_and_without_error`: validar que el literal de ayuda se mantiene visible con y sin `error_message`.

### Criterio adicional

- Debe quedar evidencia de no regresion en navegacion por flechas tras fijar la cabecera.



