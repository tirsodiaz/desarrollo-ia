## Why

La vista actual de columnas no diferencia visualmente carpetas y ficheros de forma inmediata, lo que ralentiza la navegación. Añadir iconos de tipo mejora reconocimiento y reduce errores de selección.

## What Changes

- Mostrar un icono de carpeta para cada entrada de tipo directorio en la lista de columnas.
- Mostrar un icono de fichero para cada entrada de tipo archivo en la lista de columnas.
- Mantener intactos orden, navegación por teclado y comportamiento de selección existentes.
- No introducir configuración adicional para activar/desactivar iconos en esta fase.

## Capabilities

### New Capabilities
- `file-type-icons`: representación visual por tipo de entrada (carpeta/fichero) en el explorador de columnas.

### Modified Capabilities
- Ninguna.

## Impact

- Código UI/renderizado de items en columnas.
- Posibles snapshots/tests de render si existen.
- Sin cambios de API pública ni dependencias externas obligatorias.
