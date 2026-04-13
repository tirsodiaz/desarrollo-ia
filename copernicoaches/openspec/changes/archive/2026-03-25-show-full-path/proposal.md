## Why

Actualmente la UI no muestra de forma explícita la ruta completa del directorio activo y el tamaño reportado para carpetas puede resultar incorrecto. Esto dificulta la orientación del usuario y reduce la confianza en la información mostrada en la tabla.

## What Changes

- Mostrar la ruta completa del directorio activo en una línea visible encima de la tabla de Miller Columns.
- Mantener la tabla y la navegación por teclado sin cambios funcionales; solo se añade contexto visual de ubicación.
- Corregir el cálculo de tamaño para carpetas para que refleje el tamaño agregado de su contenido de forma consistente.
- Definir comportamiento de error/permiso al calcular tamaño de carpetas, evitando bloquear la UI.

## Capabilities

### New Capabilities
- `full-path-header`: visualización de la ruta completa del directorio activo encima de la tabla.
- `accurate-folder-size`: cálculo correcto y consistente del tamaño de carpetas en la tabla.

### Modified Capabilities
- Ninguna.

## Impact

- Renderizado de cabecera/encabezado en UI de consola.
- Lógica de metadatos/tamaño en listado de entradas de carpeta.
- Posibles tests unitarios e integración sobre render y cálculo de tamaño.
- Sin cambios de API externa.