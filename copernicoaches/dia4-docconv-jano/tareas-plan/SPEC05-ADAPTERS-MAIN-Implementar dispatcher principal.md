# SPEC05-ADAPTERS-MAIN-Implementar dispatcher principal

## Descripción técnica detallada
Desarrollar `main.py` que decide entre modo CLI y MCP basado en argumentos, y `main.py` que coordina la ejecución.

## Objetivo arquitectónico
Crear el punto de entrada único que orquesta modos de ejecución, manteniendo separación entre interfaces.

## Criterios de aceptación
- `main.py` con lógica de dispatch
- Modo CLI por defecto
- Modo MCP activado con `--mcp`
- `__main__.py` ejecutable vía `python -m`

## Artefactos o entregables
- Archivos main implementados
- Tests para dispatch
- Validación de modos

## Dependencias externas e internas
- **Externas**: sys.argv parsing
- **Internas**: Adaptadores CLI y MCP

## Estimación en horas
1.5 horas