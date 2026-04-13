# Paso 3 — Visualización con Rich

## Objetivo

Implementar la capa de **visualización** que renderiza el estado en consola usando la librería Rich. Esta capa recibe el estado, no lo modifica. Cumple la regla arquitectónica: *la visualización es una proyección del estado, no su motor*.

---

## 1. Renderizador (`ui/renderer.py`)

### 1.1 Función principal `render(state, terminal_size)`

Recibe el `AppState` y las dimensiones del terminal, y dibuja la interfaz completa.

```python
def render(state: AppState, terminal_size: tuple[int, int]) -> None:
    """Renderiza el estado completo en la consola."""
    ...
```

**Componentes que dibuja:**
1. **Cabecera** — ruta absoluta del directorio actual.
2. **Tres columnas** — izquierda (padre), central (actual), derecha (preview).
3. **Separadores verticales** — líneas visibles entre columnas.
4. **Barra de estado** — mensajes de error (parte inferior).
5. **Leyenda de teclas** — ayuda rápida de navegación en una línea fija.

---

## 2. Layout de columnas

### 2.1 Distribución

- Tres columnas con proporción dinámica **1:2:2** (izquierda/centro/derecha) usando `ratio` en `rich.table.Table`.
- Las columnas se **redimensionan dinámicamente** al cambiar el tamaño del terminal.
- Mostrar separadores verticales visibles entre columnas (tabla con `box=box.SQUARE` en Rich).
- **Implementación actual:** Se usa `rich.layout.Layout` con tres regiones fijas (header, body, footer) para garantizar que cabecera y leyenda siempre son visibles.

### 2.2 Cabecera superior

- Muestra la **ruta absoluta** completa de `state.current_dir` en región fija del Layout (1 línea, siempre visible).
- Si la ruta excede el ancho del terminal, se **trunca desde la izquierda** con `…` para mantener visible el nombre del directorio actual.
- Separada visualmente de las columnas.

### 2.3 Barra de estado inferior

- Muestra `state.error_message` si existe.
- Estilo: texto en **rojo**.
- Si no hay error: la barra está vacía o no se muestra.

---

## 3. Renderizado de cada columna

### 3.1 Columna izquierda (padre/contexto) — Actualizada en iteración 3

- Siempre muestra contexto de navegación (padre/unidades según estado).
- En nivel de unidades: columna izquierda vacía.
- En raíz de unidad: listar unidades disponibles con unidad actual resaltada.
- En navegación normal: listar contenido del directorio padre con directorio actual resaltado.

### 3.2 Columna central (actual)

- Listar `state.current_contents`.
- El elemento en `state.selected_index` aparece con **inversión de color** (highlight).
- Solo los **directorios** muestran tamaño en formato humano `(B/KB/MB/GB)` en color **gris claro** (`grey70`).
- Los archivos no muestran tamaño.
- Si vacío: mostrar columna vacía.

### 3.3 Columna derecha (preview) — Actualizada en iteración 2 y 5

- Según el elemento seleccionado:
  - **Directorio:** listar sus hijos con estilos. Solo directorios muestran tamaño (gris claro).
  - **Archivo de texto:** mostrar nombre (estilo dim) y contenido completo.
  - **Archivo binario:** mostrar solo nombre.
  - **Sin selección:** columna vacía.

### 3.4 Leyenda de teclas

- Mostrar una línea fija al final del render principal:
  - `↑/↓ mover · → entrar · ← volver · Esc salir`

### 3.5 Requisito Ctrl+C

- La visualización debe coexistir con salida por `Ctrl+C` sin bloquear el loop ni dejar terminal en estado inconsistente.

---

## 4. Estilos visuales

### 4.1 Paleta de colores

| Elemento | Estilo Rich |
|----------|-------------|
| Directorio | `bold blue` |
| Archivo | color por defecto (blanco/gris) |
| Elemento seleccionado | `reverse` (inversión de color) |
| Error | `bold red` |

### 4.2 Modo degradado (terminal sin colores)

- Detectar si el terminal soporta color con `rich.console.Console.is_terminal` y capacidades de color.
- En modo degradado:
  - Directorios se muestran con prefijo `[DIR]`.
  - Selección se indica con prefijo `>`.
  - Sin estilos de color.

---

## 5. Truncamiento y scroll

### 5.1 Truncamiento de nombres

- Si un nombre excede el ancho de la columna: truncar y añadir `…` al final.
- Usar `rich.text.Text` con `overflow="ellipsis"` o implementar manualmente.

### 5.2 Scroll automático

- Calcular cuántos elementos caben en la altura disponible de la columna.
- Si `selected_index` queda fuera de la ventana visible: desplazar la ventana.
- El elemento seleccionado siempre es visible.

### 5.3 Indicadores de scroll

- Mostrar `▲` en la parte superior si hay elementos ocultos arriba.
- Mostrar `▼` en la parte inferior si hay elementos ocultos abajo.

---

## 6. Adaptación dinámica

- Detectar tamaño del terminal con `shutil.get_terminal_size()` o `rich.console.Console.size`.
- Recalcular anchos de columna y ventana de scroll en cada `render`.
- La adaptación es automática al cambiar el tamaño del terminal.

---

## 7. Tests de este paso

| Test | Verificación |
|------|-------------|
| `test_render_empty_state` | Estado con directorio vacío no lanza excepción |
| `test_render_with_contents` | Estado con elementos genera salida con nombres correctos |
| `test_truncation` | Nombre largo se trunca con `…` |
| `test_directory_style` | Directorios se renderizan con estilo `bold blue` |
| `test_selected_highlight` | Elemento seleccionado tiene estilo `reverse` |
| `test_error_message_displayed` | `error_message` aparece en la barra de estado |
| `test_scroll_indicators` | Indicadores `▲`/`▼` aparecen cuando hay contenido oculto |
| `test_parent_column_at_root` | En raíz, columna izquierda está vacía |
| `test_parent_column_highlights_current` | Directorio actual resaltado en columna izquierda |
| `test_header_shows_path` | Cabecera muestra la ruta absoluta |

> **Nota:** Los tests de renderizado pueden capturar la salida de Rich en un `StringIO` o usar `Console(file=...)` para verificar el contenido generado.

---

## 8. Criterios de validación de este paso

| # | Verificación |
|---|-------------|
| V1 | Se muestran tres columnas con el ancho correcto |
| V2 | Directorios aparecen en azul/negrita |
| V3 | El elemento seleccionado tiene inversión de color |
| V4 | La cabecera muestra la ruta absoluta |
| V5 | Nombres largos se truncan con `…` |
| V6 | Los indicadores `▲`/`▼` aparecen en directorios grandes |
| V7 | La barra de estado muestra errores en rojo |
| V8 | La columna izquierda mantiene contexto de padre/unidades |
| V9 | El renderizador funciona sin modificar el estado |
| V10 | Se muestran separadores verticales entre columnas |
| V11 | Se muestra tamaño por entrada en columnas/listados |
| V12 | Se muestra leyenda de teclas en pantalla |
| V13 | Todos los tests pasan |

---

## Trazabilidad

| Criterio de aceptación | Cubierto por |
|------------------------|-------------|
| CA01 (tres columnas) | `render` — layout de columnas |
| CA07 (distinción visual) | Estilos `bold blue` / default |
| CA08 (highlight selección) | Estilo `reverse` |
| CA09 (ruta en cabecera) | Cabecera superior |
| CA13 (truncamiento) | Truncamiento con `…` |
| CA14 (scroll + indicadores) | Scroll automático + `▲`/`▼` |
| CA17 (error en barra) | Barra de estado con `error_message` |
| CA21 (redimensionar) | Adaptación dinámica |
| CA22 (modo degradado) | Modo sin color con `[DIR]` y `>` |

---

## ✅ Estado de implementación (23 de marzo de 2026)

**Completado exitosamente con corrección de pantalla acumulada**

- ✅ `render()` implementada con `console.clear()` inicial (evita acumulación de frames)
- ✅ Tres columnas con proporción fija 20/40/40
- ✅ Cabecera con ruta absoluta
- ✅ Estilos: directorio `bold blue`, selección `reverse`, error `bold red`
- ✅ Truncamiento automático de nombres largos con `…`
- ✅ Scroll automático con indicadores `▲`/`▼` en directorios grandes
- ✅ Barra de estado inferior para errores
- ✅ Adaptación dinámica al redimensionar terminal
- ✅ Modo degradado sin colores (usa `[DIR]` y `>` para indicadores)
- ✅ Separadores verticales visibles entre columnas
- ✅ Tamaños visibles por entrada (archivos y directorios)
- ✅ Columna izquierda mantiene contexto de padre/unidades
- ✅ Columna derecha muestra contenido completo de archivo de texto seleccionado
- ✅ Leyenda de teclas en la parte inferior del render
- ✅ **10 tests renderer pasados**
- ✅ Visualización pura (no modifica estado)

**Cobertura de criterios de aceptación:** CA01, CA07, CA08, CA09, CA13, CA14, CA17, CA21, CA22

---

## Actualizaciones en iteración 2

**Cambios en visualización:**
- ✅ Columna izquierda ahora muestra unidades cuando se está en raíz de unidad
- ✅ Columna derecha ahora aplica estilos a directorios (bold blue) en preview
- ✅ Agregado soporte visual para nivel de unidades de disco
