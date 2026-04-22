# SPEC05-ADAPTERS-MCP-Implementar adaptador MCP

## Descripción técnica detallada
Desarrollar el adaptador MCP usando FastMCP que expone herramienta `convert_document` con parámetros `input_path`, `output_path` y retorna JSON con success/warnings/error.

## Objetivo arquitectónico
Crear interfaz MCP que reutiliza la misma lógica de aplicación, permitiendo integración con agentes de IA sin duplicar código.

## Criterios de aceptación
- Módulo `mcp/adapter.py` con servidor FastMCP
- Herramienta `convert_document` implementada
- Respuesta JSON según especificación
- Servidor iniciable con `--mcp`

## Artefactos o entregables
- Adaptador MCP implementado
- Configuración para VS Code
- Tests unitarios para MCP

## Dependencias externas e internas
- **Externas**: fastmcp
- **Internas**: Capa de aplicación

## Estimación en horas
2.5 horas