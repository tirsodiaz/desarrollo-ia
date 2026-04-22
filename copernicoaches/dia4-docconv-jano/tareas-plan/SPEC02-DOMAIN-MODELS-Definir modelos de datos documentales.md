# SPEC02-DOMAIN-MODELS-Definir modelos de datos documentales

## Descripción técnica detallada
Implementar los modelos de datos Pydantic para representar documentos en la capa de dominio: Document, Paragraph, Heading, List, Table, Blockquote, CodeBlock, con atributos para formato básico (bold, italic, links).

## Objetivo arquitectónico
Crear la base de datos in-memory pura para la lógica de conversión, asegurando que la capa de dominio sea completamente independiente de I/O y formatos externos.

## Criterios de aceptación
- Modelos Pydantic definidos en `src/docconv/domain/models.py`
- Estructuras jerárquicas para documentos complejos
- Atributos para formato básico (bold, italic, links)
- Validación de datos automática
- Compatibilidad con elementos soportados (RF-4, RF-5)

## Artefactos o entregables
- Archivo `models.py` con clases Pydantic
- Tests unitarios para validación de modelos
- Diagrama de clases de dominio

## Dependencias externas e internas
- **Externas**: pydantic instalado
- **Internas**: Estructura de proyecto (SPEC01)

## Estimación en horas
3 horas