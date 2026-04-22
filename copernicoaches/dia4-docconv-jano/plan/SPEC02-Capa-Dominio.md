# SPEC02 - Implementación de la Capa de Dominio

## Objetivo

Desarrollar la lógica de conversión pura entre formatos Word y Markdown, implementando la capa de dominio que contiene las reglas de negocio centrales de transformación de documentos, sin dependencias de entrada/salida.

## Descripción

La capa de dominio implementa la lógica de conversión bidireccional (Word ↔ Markdown) de manera pura y testable, siguiendo el principio de separación de responsabilidades. Esta capa no maneja archivos ni protocolos de comunicación, enfocándose únicamente en la transformación de estructuras de datos documentales. Se implementan los modelos de datos y algoritmos de conversión que preservan estructura lógica y formato básico según los requerimientos funcionales RF-4 y RF-5.

## Tareas principales

- Definir modelos de datos para documentos (`Document`, `Paragraph`, `Heading`, `List`, etc.)
- Implementar conversión DOCX → Markdown pura (sin I/O)
- Implementar conversión Markdown → DOCX pura (sin I/O)
- Crear lógica para preservación de estructura: encabezados, párrafos, listas, tablas, citas, bloques de código
- Implementar preservación de formato básico: negrita, cursiva, enlaces
- Desarrollar sistema de advertencias para elementos no soportados
- Crear tests unitarios para toda la lógica de dominio con cobertura ≥90%
- Validar conversión bidireccional sin degradación progresiva

## Dependencias

- SPEC01 completado (estructura de proyecto y toolchain configurados)
- Especificación funcional v2 (sección 4 - Requerimientos funcionales, especialmente RF-4, RF-5, RF-6)
- Guía de arquitectura (sección 3 - Principios arquitectónicos, capa de dominio)

## Riesgos y mitigaciones

- **Riesgo**: Lógica de conversión compleja puede introducir bugs difíciles de detectar.
  - **Mitigación**: Desarrollo incremental con tests unitarios exhaustivos y validación contra casos de prueba conocidos.

- **Riesgo**: Pérdida de información durante conversión bidireccional.
  - **Mitigación**: Implementar tests de round-trip (DOCX → MD → DOCX) y validar contra casos de prueba.

- **Riesgo**: Modelos de datos insuficientes para representar elementos Word/Markdown.
  - **Mitigación**: Revisar especificaciones de formatos y extender modelos según necesidad, manteniendo compatibilidad.

## Resultado/Entregable esperado

- Módulo `src/docconv/domain/` completamente implementado con conversión pura
- Tests unitarios pasando con cobertura ≥90% en capa de dominio
- Funciones `docx_to_markdown()` y `markdown_to_docx()` operativas sin I/O
- Sistema de advertencias implementado para elementos degradados
- Validación de preservación de estructura y formato básico
- Documentación técnica de algoritmos de conversión