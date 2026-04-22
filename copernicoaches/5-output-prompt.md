---
name: generate-implementation-code
agent: analyst-programmer-agent
output_format: code_files
---
# Instrucción de Generación: Código de Implementación

Genera código funcional, paso a paso, basado en el plan de implementación y tareas proporcionadas.

## Criterios de Codificación
- **Exactitud:** Codificar solo lo especificado en el plan; no inventar.
- **Modularidad:** Código limpio, legible, comentado y estructurado.
- **Dependencias:** Respetar frameworks, librerías y lenguajes especificados.
- **Buenas Prácticas:** Seguir convenciones del lenguaje objetivo.

## Flujo de Trabajo
1. Analizar plan/tareas como contexto inicial.
2. Codificar paso a paso siguiendo el orden del plan.
3. Incluir comentarios explicativos y buenas prácticas.
4. Producir código solo necesario para cumplir objetivo.
5. Esperar confirmación antes de continuar con siguiente paso.
6. Plantear dudas antes de codificar si hay ambigüedad.

## Restricciones de Estilo
- Usar lenguaje especificado o solicitar antes de empezar.
- Indicar claramente ambigüedades o información faltante.
- No proponer soluciones no aprobadas.
- Usar carpeta indicada o preguntar antes de generar código.

## Salida Esperada
Código funcional y documentado generado iterativamente hasta completar plan de implementación.
