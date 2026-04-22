# SPEC03-INFRA-WRITERS-Implementar escritor de archivos DOCX

## Descripción técnica detallada
Desarrollar función `write_docx(document, file_path)` que toma estructura de dominio Document y genera archivo .docx válido.

## Objetivo arquitectónico
Implementar interfaz de salida para formato DOCX, completando el ciclo de I/O.

## Criterios de aceptación
- Función `write_docx()` en `infrastructure/writer.py`
- Generación de archivos .docx válidos
- Preservación de estructura y formato
- Manejo de errores de escritura

## Artefactos o entregables
- Función de escritura DOCX
- Tests de integración con round-trip
- Validación de archivos generados

## Dependencias externas e internas
- **Externas**: python-docx
- **Internas**: Modelos de dominio

## Estimación en horas
2.5 horas