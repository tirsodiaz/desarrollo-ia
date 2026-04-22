# SPEC03-INFRA-READERS-Implementar lector de archivos DOCX

## Descripción técnica detallada
Desarrollar función `read_docx(file_path)` que lee archivo .docx y lo convierte a estructura de dominio Document, usando python-docx para parsing.

## Objetivo arquitectónico
Implementar la interfaz de infraestructura para entrada de datos, aislando operaciones I/O de la lógica de dominio.

## Criterios de aceptación
- Función `read_docx()` en `infrastructure/reader.py`
- Conversión correcta a modelos de dominio
- Manejo de errores de archivo (no existe, corrupto)
- Compatibilidad con elementos soportados

## Artefactos o entregables
- Función de lectura implementada
- Tests de integración para casos válidos/inválidos
- Documentación de formatos DOCX soportados

## Dependencias externas e internas
- **Externas**: python-docx
- **Internas**: Modelos de dominio

## Estimación en horas
2.5 horas