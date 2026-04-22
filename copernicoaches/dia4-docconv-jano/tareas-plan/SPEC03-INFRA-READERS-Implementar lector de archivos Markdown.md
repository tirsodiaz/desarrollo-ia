# SPEC03-INFRA-READERS-Implementar lector de archivos Markdown

## Descripción técnica detallada
Desarrollar función `read_markdown(file_path)` que lee archivo .md y lo convierte a estructura de dominio Document, usando markdown-it-py para parsing.

## Objetivo arquitectónico
Completar la interfaz de entrada de datos, manteniendo consistencia con el lector DOCX.

## Criterios de aceptación
- Función `read_markdown()` implementada
- Parsing correcto de sintaxis Markdown
- Conversión a modelos de dominio
- Manejo de archivos de texto plano

## Artefactos o entregables
- Función de lectura Markdown
- Tests de integración
- Validación de sintaxis soportada

## Dependencias externas e internas
- **Externas**: markdown-it-py
- **Internas**: Modelos de dominio

## Estimación en horas
2 horas