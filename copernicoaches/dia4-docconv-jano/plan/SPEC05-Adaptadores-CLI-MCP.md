# SPEC05 - Implementación de Adaptadores CLI y MCP

## Objetivo

Desarrollar los adaptadores de interfaz que permiten ejecutar la aplicación tanto desde línea de comandos (CLI) como servicio MCP, compartiendo la misma lógica de aplicación sin duplicaciones.

## Descripción

Los adaptadores implementan las interfaces externas del sistema, manteniéndose ligeros y enfocados únicamente en protocolos de comunicación. El adaptador CLI maneja argumentos de línea de comandos y salida por stdio, mientras que el adaptador MCP expone la funcionalidad como herramientas para agentes de IA. Ambos reutilizan la capa de aplicación implementada en pasos anteriores.

## Tareas principales

- Implementar adaptador CLI (`src/docconv/cli/`) con parseo de argumentos
- Crear punto de entrada CLI que llame a `convert_file()` de aplicación
- Implementar salida por stdout/stderr según especificación
- Desarrollar adaptador MCP (`src/docconv/mcp/`) usando FastMCP
- Crear herramienta `convert_document` con parámetros `input_path` y `output_path`
- Implementar respuesta JSON del MCP con `success`, `warnings` y `error`
- Configurar modo `--mcp` en `main.py` para activar servidor MCP
- Crear tests end-to-end para ambos modos de ejecución
- Validar consistencia entre CLI y MCP

## Dependencias

- SPEC01 a SPEC04 completados (toda la lógica de aplicación implementada)
- Especificación funcional v2 (sección 7.2 - Modos de ejecución, RF-2, RF-3, RF-8)
- Guía de arquitectura (sección 4 - Execution Model, sección 8 - MCP Integration)

## Riesgos y mitigaciones

- **Riesgo**: Duplicación de lógica entre adaptadores.
  - **Mitigación**: Ambos adaptadores llaman únicamente a la capa de aplicación, sin lógica propia.

- **Riesgo**: Diferencias en comportamiento entre CLI y MCP.
  - **Mitigación**: Tests end-to-end que validen ambos modos con los mismos casos de prueba.

- **Riesgo**: Configuración MCP compleja o incompatible.
  - **Mitigación**: Seguir exactamente la guía de arquitectura y usar FastMCP como recomendado.

## Resultado/Entregable esperado

- Adaptadores CLI y MCP completamente funcionales
- Comando `docconv input.docx output.md` operativo desde línea de comandos
- Comando `docconv --mcp` inicia servidor MCP correctamente
- Tests end-to-end pasando para ambos modos
- Consistencia verificada entre interfaces CLI y MCP
- Documentación de uso para ambos modos de ejecución