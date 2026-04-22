# SPEC04-APP-TESTING-Desarrollar tests de integración de aplicación

## Descripción técnica detallada
Crear tests que validen la orquestación completa de la capa de aplicación, incluyendo integración con dominio e infraestructura.

## Objetivo arquitectónico
Asegurar que la capa de aplicación coordina correctamente las demás capas, siguiendo estándares de testing.

## Criterios de aceptación
- Tests en `tests/integration/` para aplicación
- Validación de flujos completos
- Tests con mocks para I/O si necesario
- Cobertura de casos de éxito y error

## Artefactos o entregables
- Tests de integración de aplicación
- Validación de orquestación correcta

## Dependencias externas e internas
- **Externas**: pytest
- **Internas**: Función convert_file implementada

## Estimación en horas
2 horas