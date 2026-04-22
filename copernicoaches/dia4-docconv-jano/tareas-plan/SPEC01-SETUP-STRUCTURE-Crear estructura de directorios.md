# SPEC01-SETUP-STRUCTURE-Crear estructura de directorios

## Descripción técnica detallada
Crear la estructura de directorios completa del proyecto siguiendo la guía de arquitectura (sección 6.2), incluyendo src/docconv/ con subdirectorios para capas, tests/ con tipos de pruebas, y archivos base como __main__.py y main.py.

## Objetivo arquitectónico
Establecer la arquitectura en capas obligatoria con separación clara de responsabilidades: entrypoint, CLI adapter, MCP adapter, application layer, domain layer, infrastructure layer.

## Criterios de aceptación
- Directorio `src/docconv/` creado con subcarpetas: cli/, mcp/, application/, domain/, infrastructure/
- Directorio `tests/` creado con subcarpetas: unit/, integration/, e2e/
- Archivos base `__main__.py` y `main.py` creados
- Estructura alineada con guía de arquitectura
- Archivos __init__.py en paquetes Python

## Artefactos o entregables
- Estructura de directorios completa
- Archivos base con imports mínimos
- Diagrama de arquitectura actualizado (si aplica)

## Dependencias externas e internas
- **Externas**: Sistema de archivos operativo
- **Internas**: pyproject.toml configurado

## Estimación en horas
1.5 horas