# Backlog de Implementación - docconv

## Resumen Ejecutivo

Este backlog detalla las tareas de implementación para el proyecto `docconv`, un conversor bidireccional de documentos Word ↔ Markdown. El proyecto sigue una arquitectura en capas estricta con adaptadores CLI y MCP.

**Total de tareas:** 22
**Estimación total:** ~55 horas
**Duración estimada:** 3-4 semanas (equipo de 2-3 desarrolladores)

## Estructura por Épicas

### 🎯 SPEC01 - Configuración del Proyecto (6 tareas, ~7.5 horas)
- Configuración de toolchain y dependencias
- Estructura de directorios según arquitectura
- Setup de testing y calidad de código
- Documentación inicial

### 🧠 SPEC02 - Capa de Dominio (5 tareas, ~13 horas)
- Modelos de datos Pydantic para documentos
- Lógica de conversión DOCX → Markdown
- Lógica de conversión Markdown → DOCX
- Sistema de advertencias para elementos no soportados
- Suite completa de tests unitarios

### 🔌 SPEC03 - Capa de Infraestructura (5 tareas, ~8.5 horas)
- Lectores de archivos (DOCX y Markdown)
- Escritores de archivos (DOCX y Markdown)
- Validación de archivos de entrada
- Tests de integración I/O

### 🎼 SPEC04 - Capa de Aplicación (2 tareas, ~5 horas)
- Función principal de orquestación `convert_file()`
- Tests de integración de aplicación

### 🌐 SPEC05 - Adaptadores CLI y MCP (4 tareas, ~9 horas)
- Implementación de adaptador CLI
- Implementación de adaptador MCP con FastMCP
- Dispatcher principal para modos de ejecución
- Tests end-to-end completos

### 🏗️ Arquitectura (3 tareas, ~5.5 horas)
- Diagramas C4 y de secuencia
- Architecture Decision Records (ADR)
- Pipeline de validación de integración

## Dependencias Críticas

1. **SPEC01** debe completarse antes de cualquier desarrollo
2. **SPEC02** es prerrequisito para SPEC03 y SPEC04
3. **SPEC03** debe completarse antes de SPEC04
4. **SPEC04** es necesario para SPEC05
5. **Arquitectura** puede desarrollarse en paralelo pero requiere validación final

## Métricas de Calidad

- **Cobertura de tests:** ≥90% total, ≥95% en dominio
- **Linting:** 0 errores de ruff
- **Round-trip stability:** Conversión bidireccional sin degradación
- **Consistencia CLI/MCP:** Misma lógica, mismos resultados

## Riesgos y Mitigaciones

- **Riesgo técnico:** Complejidad de parsing Word/Markdown
  - **Mitigación:** Desarrollo incremental con tests exhaustivos

- **Riesgo de alcance:** Elementos avanzados de Word no soportados
  - **Mitigación:** Enfoque en elementos estándar, documentación de limitaciones

- **Riesgo de integración:** CLI vs MCP inconsistentes
  - **Mitigación:** Tests end-to-end que validan ambos modos

## Criterios de Aceptación Global

- ✅ Conversión bidireccional funcional
- ✅ Preservación de estructura lógica y formato básico
- ✅ Modos CLI y MCP operativos
- ✅ Reporte de advertencias transparente
- ✅ Cobertura de tests ≥90%
- ✅ Pipeline de validación automatizado
- ✅ Documentación completa (README, ADR, diagramas)

## Notas de Implementación

- **Tecnologías:** Python 3.11+, uv, FastMCP, pytest, ruff
- **Arquitectura:** Capas estrictas (domain → infrastructure → application → adapters)
- **Testing:** Unit (dominio), Integration (I/O + app), E2E (CLI + MCP)
- **Calidad:** Linting obligatorio, formatting automático, cobertura medida

Este backlog está estructurado para desarrollo incremental con validación continua, permitiendo entregas parciales funcionales en cada SPEC.