---
name: generate-functional-spec-v3
agent: iterative-analyst-agent
output_name: "Especificación Funcional (dudas resueltas) – v3.md"
---
# Instrucción de Redacción Final

Genera el documento de especificación funcional utilizando únicamente la información validada durante la fase iterativa.

## Estructura Obligatoria
1. **Título y Versión:** (Especificación Funcional - v3).
2. **Índice.**
3. **Contexto del Proyecto.**
4. **Alcance (In/Out):** Detallar qué se incluye y qué queda fuera.
5. **Requisitos Funcionales Detallados.**
6. **Reglas de Negocio:** Listado numerado de normas lógicas.
7. **Flujos/Diagramas:** Representación en formato texto (Mermaid o similar).
8. **Validaciones:** Listado de hipótesis que fueron validadas o descartadas.
9. **Puntos Pendientes:** Solo si hubo bloqueos externos no resueltos.

## Restricciones de Estilo
- Usa un tono formal y corporativo.
- Marca cada punto incierto con las etiquetas obligatorias: [Pendiente de validar], [Hipótesis], [Dependencia].
- No incluyas conclusiones genéricas; sé específico con la documentación analizada.
- No inventes información; basa todo en datos validados.