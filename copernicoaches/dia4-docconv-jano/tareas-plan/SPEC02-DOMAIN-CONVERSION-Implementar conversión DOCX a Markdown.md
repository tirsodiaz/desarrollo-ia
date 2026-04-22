# SPEC02-DOMAIN-CONVERSION-Implementar conversión DOCX a Markdown

## Descripción técnica detallada
Desarrollar la función pura `docx_to_markdown()` que convierte estructuras de documento DOCX a sintaxis Markdown, preservando encabezados, párrafos, listas, tablas, citas, bloques de código y formato básico.

## Objetivo arquitectónico
Implementar la lógica de conversión bidireccional pura en la capa de dominio, asegurando que la transformación sea determinística y testable sin dependencias externas.

## Criterios de aceptación
- Función `docx_to_markdown(document)` implementada
- Preservación de estructura lógica completa
- Formato Markdown válido (GFM compatible)
- Manejo de elementos anidados (listas, tablas)
- Cobertura de tests unitarios ≥90%

## Artefactos o entregables
- Función de conversión en `docx_to_md.py`
- Tests unitarios exhaustivos
- Casos de prueba para elementos complejos

## Dependencias externas e internas
- **Externas**: Ninguna (lógica pura)
- **Internas**: Modelos de datos definidos

## Estimación en horas
4 horas