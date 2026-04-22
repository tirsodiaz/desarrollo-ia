---
name: generate-functional-spec-v2
agent: functional-analyst-agent
output_format: markdown
version: "Especificación Funcional (con dudas) – v2"
---
# Instrucción de Redacción: Documento V2

Genera el documento final utilizando los datos procesados por `analyst-skills`.

## Estructura Obligatoria
1. **Índice de Contenidos.**
2. **Introducción y Contexto:** Origen del proyecto.
3. **Objetivo del Documento.**
4. **Alcance Funcional:** Definición clara de *In-scope* y *Out-of-scope*.
5. **Historias de Usuario:** (Generadas como PO si no existen).
6. **Descripción de Requerimientos y Reglas de Negocio.**
7. **Supuestos e Hipótesis:** Basados en falta de información.
8. **Sección de Dudas y Riesgos:** Preguntas concretas para el equipo técnico/negocio y bloqueos derivados.

## Restricciones de Estilo
- Usa un tono formal y corporativo.
- Marca cada punto incierto con etiquetas: [Duda], [Hipótesis a validar], etc.
- No incluyas conclusiones genéricas; sé específico con la documentación analizada.