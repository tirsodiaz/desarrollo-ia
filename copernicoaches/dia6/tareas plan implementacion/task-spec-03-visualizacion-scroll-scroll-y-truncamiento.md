# SPEC-03 | VISUALIZACION | SCROLL | Scroll automÃ¡tico y truncamiento de nombres

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-03-visualizacion-scroll-scroll-y-truncamiento |
| **CÃ³digo de plan** | SPEC-03 |
| **Ã‰pica** | VISUALIZACION â€” VisualizaciÃ³n con Rich |
| **Feature** | SCROLL â€” Scroll virtual y truncamiento de texto |
| **Tipo** | Tarea tÃ©cnica â€” Capa de presentaciÃ³n |
| **Prioridad** | Alta |
| **EstimaciÃ³n** | 3 h |

---

## DescripciÃ³n tÃ©cnica

Implementar dentro de `ui/renderer.py` las funcionalidades de scroll virtual por columna y truncamiento inteligente de nombres de archivo, garantizando usabilidad en cualquier tamaÃ±o de terminal.

### Truncamiento de nombres (CA13)

- Usar `rich.text.Text.truncate(max_width, overflow="ellipsis")` para aÃ±adir `â€¦` al final.
- El sufijo de tamaÃ±o en `grey70` (ej. `(4.2 KB)`) se reserva dentro del ancho disponible y **nunca** se trunca ni omite.
- El ancho disponible = ancho de columna - len(sufijo_tamaÃ±o) - separador.

### Ventana de scroll (CA14)

```python
def _scroll_window(contents, selected_index, column_height):
    visible = min(len(contents), column_height)
    offset = max(0, selected_index - visible + 1)
    return contents[offset : offset + visible], offset
```

- `scroll_offset` se calcula en cada frame; **no** se almacena en `AppState`.
- El elemento seleccionado siempre queda dentro de la ventana visible.
- `column_height` = `terminal_height - header_lines - footer_lines`.

### Indicadores de scroll

| CondiciÃ³n | Indicador |
|-----------|-----------|
| `offset > 0` | `â–²` en primera lÃ­nea de la columna (`grey70`) |
| `offset + visible < len(contents)` | `â–¼` en Ãºltima lÃ­nea de la columna (`grey70`) |
| Sin elementos ocultos | Sin indicadores |

### AdaptaciÃ³n dinÃ¡mica (CA21)

- Detectar tamaÃ±o con `console.size` en cada llamada a `render()`.
- Recalcular anchos de columna y ventana en cada frame.
- No cachear dimensiones entre frames.

---

## Objetivo arquitectÃ³nico

Garantizar que la **Capa 4** es robusta ante condiciones reales de uso: terminales pequeÃ±as, directorios grandes, cambios de tamaÃ±o en tiempo de ejecuciÃ³n. Un renderizador que falla en estas condiciones degradarÃ­a la experiencia mÃ¡s que cualquier bug en capas internas.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | Nombre de 100 chars en columna de 20 chars â†’ truncado con `â€¦` |
| CA-2 | Elemento seleccionado siempre visible sin importar cuÃ¡ntos elementos haya |
| CA-3 | `â–²` aparece cuando hay elementos ocultos arriba |
| CA-4 | `â–¼` aparece cuando hay elementos ocultos abajo |
| CA-5 | Sin indicadores de scroll cuando todos los elementos caben |
| CA-6 | Al cambiar `terminal_size`, el scroll se recalcula correctamente |
| CA-7 | El sufijo de tamaÃ±o nunca queda truncado ni omitido |

---

## Artefactos y entregables

- Funciones helper `_scroll_window` y `_truncate_name` en `ui/renderer.py`
- Tests `test_truncation`, `test_scroll_indicators` en `tests/test_renderer.py`

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-03-VISUALIZACION-RENDERER (renderer base implementado) |
| **Bloquea** | SPEC-03-VISUALIZACION-TESTING |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| Altura de columna imprecisa al incluir bordes de tabla Rich | Medir empÃ­ricamente con `Console(file=StringIO(), height=N)` en test |
| Nombres con caracteres Unicode anchos (CJK) | Usar `rich.cells.cell_len` en lugar de `len()` para medir ancho real |
| Scroll inconsistente al cambiar de directorio | `offset` calculado siempre desde cero basado en `selected_index` actual |

---

## Actualizacion OpenSpec 2026-03-27

### Requisitos adicionales de scroll

- Scroll descendente: al avanzar, los elementos superiores salen de ventana y aparecen nuevos elementos inferiores.
- Scroll ascendente: al retroceder, reaparecen progresivamente los elementos previos y salen los inferiores.
- La cabecera de ruta debe permanecer fija y visible durante ambos sentidos de scroll.

### Ajustes en criterios de aceptacion

- Incluir prueba explicita de bloques dinamicos visibles en navegacion hacia abajo.
- Incluir prueba explicita de recuperacion progresiva al navegar hacia arriba.



