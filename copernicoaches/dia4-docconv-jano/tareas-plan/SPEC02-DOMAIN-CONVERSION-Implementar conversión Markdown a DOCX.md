# SPEC02-DOMAIN-CONVERSION-Implementar conversión Markdown a DOCX

## Descripción técnica detallada
Desarrollar la función pura `markdown_to_docx()` que convierte sintaxis Markdown a estructuras de documento DOCX, preservando encabezados, párrafos, listas, tablas, citas, bloques de código y formato básico.

## Objetivo arquitectónico
Completar la lógica de conversión bidireccional pura, asegurando simetría en las transformaciones y consistencia en el manejo de elementos.

## Criterios de aceptación
- Función `markdown_to_docx(markdown_text)` implementada
- Parsing correcto de sintaxis Markdown (CommonMark)
- Generación de estructuras DOCX válidas
- Preservación de formato básico
- Tests unitarios con cobertura ≥90%

## Artefactos o entregables
- Función de conversión en `md_to_docx.py`
- Tests unitarios para parsing Markdown
- Validación de estructuras DOCX generadas

## Dependencias externas e internas
- **Externas**: markdown-it-py para parsing (si necesario, pero preferir implementación pura)
- **Internas**: Modelos de datos y conversión DOCX→MD

## Estimación en horas
4 horas