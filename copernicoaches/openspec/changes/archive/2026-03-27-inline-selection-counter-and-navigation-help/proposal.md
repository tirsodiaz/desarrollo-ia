## Why

La UI de consola muestra el contador del elemento seleccionado (por ejemplo `[7/7]`) en una línea separada, lo que dificulta la lectura rápida del estado actual. Además, la ayuda de navegación no está definida de forma consistente para las acciones clave (mover, entrar, volver, salir).

## What Changes

- Mostrar el contador de selección en la misma línea del estado/cabecera de navegación, nunca en la línea siguiente.
- Estandarizar y mostrar las ayudas de teclado visibles para navegación: `up/down mover`, `. entrar`, `<- volver`, `Esc salir`.
- Ajustar el renderizado para mantener la disposición en una sola línea incluso con cambios de selección y redimensionado.
- Añadir/actualizar pruebas de renderizado para validar formato de línea y textos de ayuda.

## Capabilities

### New Capabilities
- `inline-selection-status-and-navigation-hints`: Define el formato visible de cabecera para incluir `[n/N]` en la misma línea y los atajos de navegación obligatorios.

### Modified Capabilities
- Ninguna.

## Impact

- Código afectado: módulo de render (`src/miller/ui/renderer.py`) y potencialmente wiring de entrada (`src/miller/ui/input_handler.py`) solo si requiere sincronización de textos.
- Pruebas afectadas: tests de renderer e integración (`tests/test_renderer.py`, `tests/test_integration.py`, y/o tests de comportamiento de cabecera).
- Sin cambios de API externa ni dependencias nuevas.
