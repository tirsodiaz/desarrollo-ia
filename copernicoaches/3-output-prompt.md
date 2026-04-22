---
name: generate-implementation-plan
agent: architect-plan-agent
output_format: multiple_markdown_files
---
# Instrucción de Generación: Plan de Implementación

Genera un conjunto de archivos .md, uno por cada paso del plan (máximo 5), utilizando datos de architect-planning-skills.

## Estructura por Archivo .md
- **Título del Paso**
- **Objetivo**
- **Descripción**
- **Tareas Principales**
- **Dependencias**
- **Riesgos y Mitigaciones**
- **Resultado/Entregable Esperado**

## Restricciones de Estilo
- Lenguaje profesional, técnico y de arquitectura.
- Nombres de archivos: SPEC01-xxxx.md, etc., indicando el paso.
- No inventar información; marcar "Información no disponible" si falta.
- Al finalizar análisis, decir “Plan listo.”