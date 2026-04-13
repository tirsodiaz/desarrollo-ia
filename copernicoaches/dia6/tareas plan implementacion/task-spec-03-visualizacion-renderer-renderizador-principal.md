# SPEC-03 | VISUALIZACION | RENDERER | Implementar renderizador principal (renderer.py)

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-03-visualizacion-renderer-renderizador-principal |
| **CÃ³digo de plan** | SPEC-03 |
| **Ã‰pica** | VISUALIZACION â€” VisualizaciÃ³n con Rich |
| **Feature** | RENDERER â€” Renderizador de columnas (Capa 4) |
| **Tipo** | Tarea tÃ©cnica â€” Capa de presentaciÃ³n |
| **Prioridad** | CrÃ­tica |
| **EstimaciÃ³n** | 6 h |

---

## DescripciÃ³n tÃ©cnica

Implementar `render(state: AppState) -> None` en `ui/renderer.py`. Recibe el `AppState` y proyecta la interfaz completa en la consola usando Rich. **Nunca modifica el estado.**

### Layout estructural

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ HEADER (1 lÃ­nea) â€” ruta absoluta de current_dir â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  IZQUIERDA   â”‚    CENTRAL       â”‚   DERECHA     â”‚
â”‚  ratio=1     â”‚    ratio=2       â”‚   ratio=2     â”‚
â”‚  (padre /    â”‚  (dir actual)    â”‚  (preview)    â”‚
â”‚   unidades)  â”‚                  â”‚               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ FOOTER (1 lÃ­nea) â€” error  +  ayuda+contador inline â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

ImplementaciÃ³n con `rich.layout.Layout` + tres regiones fijas (header, body, footer). Body contiene `rich.table.Table` con `box=box.SQUARE` para separadores verticales visibles. Cada frame comienza con `console.clear()`.

### Columna izquierda (contexto navegaciÃ³n)

| CondiciÃ³n | Contenido |
|-----------|-----------|
| `is_at_drives=True` | VacÃ­a |
| `parent_dir is None` (raÃ­z de unidad) | Lista de unidades con unidad actual en `reverse` |
| NavegaciÃ³n normal | Contenido del directorio padre con directorio actual en `reverse` |

### Columna central (directorio actual)

- Listar `state.current_contents`.
- Elemento en `selected_index` con estilo `reverse`.
- Directorios: tamaÃ±o en formato humano `(B/KB/MB/GB)` en `grey70`.
- Archivos: sin tamaÃ±o.
- Si vacÃ­o: columna vacÃ­a.

### Columna derecha (preview)

| Elemento seleccionado | Contenido |
|-----------------------|-----------|
| Directorio | Listar hijos con estilos; dirs muestran tamaÃ±o |
| Archivo de texto | Nombre en `dim` + contenido completo |
| Archivo binario | Solo nombre |
| Sin selecciÃ³n (`-1`) | VacÃ­a |

### Cabecera

- Ruta absoluta `str(state.current_dir)`.
- Si excede ancho del terminal: truncar desde la izquierda con prefijo `â€¦`.

### Footer

- `error_message` en `bold red` si existe.
- LÃ­nea fija de ayuda: `up/down mover . -> entrar . <- volver . Esc salir [n/N]`
- El contador `[n/N]` debe renderizarse en la misma lÃ­nea de ayuda (no en lÃ­nea independiente).

### Paleta de estilos

| Elemento | Estilo Rich |
|----------|-------------|
| Directorio | `bold blue` |
| Archivo | default |
| Seleccionado | `reverse` |
| Error | `bold red` |
| TamaÃ±o | `grey70` |
| Preview: nombre archivo | `dim` |

### Modo degradado (sin color)

- Directorios: prefijo `[DIR]`
- SelecciÃ³n: prefijo `>` en lugar de `reverse`

---

## Objetivo arquitectÃ³nico

Implementar la **Capa 4 (VisualizaciÃ³n)** como **funciÃ³n pura de proyecciÃ³n**: dado el mismo estado siempre produce el mismo output visual. NingÃºn componente puede distinguir si el estado llegÃ³ de una acciÃ³n real o de un test â€” propiedad que hace al renderer 100% testeable de forma aislada.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | Tres columnas con separadores verticales visibles (ratio 1:2:2) |
| CA-2 | Directorios en `bold blue`; archivos en color por defecto |
| CA-3 | Elemento en `selected_index` con inversiÃ³n de color |
| CA-4 | Cabecera muestra la ruta absoluta de `current_dir` |
| CA-5 | Footer muestra `error_message` en `bold red` cuando no es `None` |
| CA-6 | LÃ­nea de ayuda visible en la parte inferior con contador inline `[n/N]` |
| CA-7 | Columna izquierda vacÃ­a cuando `is_at_drives=True` |
| CA-8 | Columna derecha muestra preview del elemento seleccionado |
| CA-9 | El renderer NO modifica ningÃºn campo de `AppState` |
| CA-10 | Sin excepciÃ³n cuando `current_contents` estÃ¡ vacÃ­o |
| CA-11 | TamaÃ±os en `grey70` para dirs/archivos |
| CA-12 | Modo degradado: `[DIR]` y `>` cuando no hay soporte de color |

---

## Artefactos y entregables

- `src/miller/ui/renderer.py` con `render()` completamente implementada
- `tests/test_renderer.py` (ver SPEC-03-VISUALIZACION-TESTING)

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-01-DOMINIO-MODELO (`AppState`, `FileEntry` como tipos de entrada) |
| **Externa** | `rich >= 13.0` instalado |
| **Bloquea** | SPEC-03-VISUALIZACION-SCROLL (scroll se implementa dentro del renderer) |
| **Bloquea** | SPEC-03-VISUALIZACION-TESTING |
| **Bloquea** | SPEC-04-INTEGRACION-MAIN |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| Columna izquierda requiere contenidos del padre no en `AppState` | Evaluar aÃ±adir `parent_contents: list[FileEntry]` a `AppState` o calcular en renderer |
| Parpadeo por `console.clear()` en terminales lentos | Usar `console.screen()` en el bucle principal (buffer alternativo) |
| Terminal muy estrecho (<80 cols) desborda columnas | Definir ancho mÃ­nimo y mostrar advertencia si es menor |

---

## Actualizacion OpenSpec 2026-03-27

### Requisitos adicionales

- El header con ruta completa debe permanecer siempre visible durante scroll vertical.
- Solo el cuerpo de columnas puede ser region desplazable.
- No se permite regresion en comportamiento de navegacion por flechas.

### Ajustes de aceptacion para esta tarea

- Agregar validacion especifica de invariante de layout: header/footer fijos y body scrolleable.
- Confirmar que el renderer mantiene la ruta sincronizada con `state.current_dir` en cada frame.
- Confirmar que la ayuda visible usa el literal `up/down mover . -> entrar . <- volver . Esc salir`.
- Confirmar que el contador de selecciÃ³n se muestra como sufijo inline ` [n/N]`.



