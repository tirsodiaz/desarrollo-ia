## Context

Actualmente el renderer arma el `footer` con dos líneas cuando hay selección: la primera contiene la ayuda (`up/down mover . -> entrar . <- volver . Esc salir`) y la segunda el contador (`[n/N]`). Esto provoca que el estado de selección quede separado visualmente del contexto principal. El cambio requiere una presentación consistente donde el contador aparezca en la misma línea del estado visible, sin introducir nuevas dependencias ni cambios en navegación de dominio.

## Goals / Non-Goals

**Goals:**
- Mostrar siempre el contador de selección `[n/N]` en la misma línea de estado (header), nunca en línea separada.
- Mantener visible y consistente el texto de ayuda de navegación: `up/down mover . -> entrar . <- volver . Esc salir`.
- Preservar compatibilidad con el layout existente de Rich y terminales Windows/PowerShell.
- Cubrir el cambio con pruebas de renderer/integración centradas en formato de salida.

**Non-Goals:**
- Cambiar el mapeo de teclas o semántica de `input_handler`.
- Rediseñar columnas, iconografía o estilos de color.
- Incorporar i18n o parametrización de textos de ayuda en esta iteración.

## Decisions

1. Contador movido a header.
- Decisión: construir el header como una línea compuesta que incluya ruta/estado y sufijo de posición ` [n/N]` cuando exista selección.
- Rationale: el header ya representa el contexto actual (ruta o unidades), por lo que agregar posición ahí evita duplicidad y elimina saltos de línea innecesarios en el footer.
- Alternativas consideradas:
  - Mantener contador en footer y unir con texto de ayuda: descartado por reducir legibilidad y dificultar truncado de la ayuda.
  - Añadir una nueva barra de estado dedicada: descartado por mayor complejidad de layout para un cambio acotado.

2. Footer de una sola responsabilidad.
- Decisión: dejar el footer para ayuda (y errores cuando existan), quitando el contador de esa sección.
- Rationale: separar responsabilidades facilita pruebas y evita crecimiento dinámico de líneas por selección.
- Alternativas consideradas:
  - Footer multilinea fijo: descartado por desperdicio de espacio vertical en terminales pequeñas.

3. Reglas de truncado en header.
- Decisión: aplicar truncado sobre la línea completa de estado para garantizar que ruta + contador no desborden ancho.
- Rationale: si se trunca solo la ruta sin considerar el contador, puede romperse el objetivo de mantener `[n/N]` visible en la misma línea.
- Alternativas consideradas:
  - Truncar al final de toda la línea sin priorizar contador: descartado porque puede ocultar el contador.

4. Estrategia de pruebas.
- Decisión: agregar/ajustar tests que validen que el contador aparece inline con el header y que no queda como línea independiente en footer.
- Rationale: el riesgo principal es un ajuste visual que pase manualmente pero falle en regresiones de render.

## Risks / Trade-offs

- [Riesgo] ANSI/estilos de Rich dificultan aserciones directas de línea exacta. -> Mitigación: normalizar salida removiendo secuencias ANSI en tests y validar patrones textuales.
- [Riesgo] En anchos muy pequeños puede perderse parte de ruta o ayuda. -> Mitigación: priorizar visibilidad del contador y mantener truncado elíptico de ruta.
- [Trade-off] Menos información vertical en footer a cambio de header más cargado. -> Mitigación: formato compacto y predecible con separador fijo.

## Migration Plan

- Implementar ajuste en `renderer` sin cambiar interfaces públicas.
- Ejecutar suite de tests del módulo `renderer` e integración.
- Si se detecta regresión visual, rollback directo del cambio de composición de header/footer.

## Open Questions

- ¿El contador debe mostrarse también en estado de unidades (`is_at_drives`) cuando haya selección, o solo en listas de contenido? Se propone mostrarlo siempre que `selected_index >= 0` y haya elementos visibles.
