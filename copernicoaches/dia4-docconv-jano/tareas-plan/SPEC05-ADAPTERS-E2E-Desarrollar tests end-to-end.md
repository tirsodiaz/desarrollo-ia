# SPEC05-ADAPTERS-E2E-Desarrollar tests end-to-end

## Descripción técnica detallada
Crear tests que ejecutan el comando completo desde línea de comandos y validan MCP, incluyendo archivos reales.

## Objetivo arquitectónico
Validar integración completa del sistema, asegurando que CLI y MCP funcionen idénticamente.

## Criterios de aceptación
- Tests en `tests/e2e/` para subprocess calls
- Validación de archivos generados
- Tests de round-trip completos
- Cobertura de casos de error

## Artefactos o entregables
- Tests end-to-end
- Archivos de prueba para validación
- Reporte de cobertura total ≥90%

## Dependencias externas e internas
- **Externas**: subprocess para ejecución
- **Internas**: Todo el sistema implementado

## Estimación en horas
3 horas