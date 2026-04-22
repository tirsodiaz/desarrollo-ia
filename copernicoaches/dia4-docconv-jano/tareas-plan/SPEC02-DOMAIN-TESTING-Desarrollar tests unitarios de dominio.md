# SPEC02-DOMAIN-TESTING-Desarrollar tests unitarios de dominio

## Descripción técnica detallada
Crear suite completa de tests unitarios para la capa de dominio, cubriendo modelos, conversiones y advertencias con cobertura ≥90%.

## Objetivo arquitectónico
Asegurar calidad y corrección de la lógica de negocio pura mediante testing exhaustivo, siguiendo estándares de arquitectura (sección 6.4).

## Criterios de aceptación
- Tests en `tests/unit/` para toda lógica de dominio
- Cobertura ≥90% en capa de dominio
- Tests de round-trip (conversión bidireccional)
- Tests para casos edge y errores

## Artefactos o entregables
- Archivos de test unitarios
- Reporte de cobertura pytest-cov
- Casos de prueba documentados

## Dependencias externas e internas
- **Externas**: pytest configurado
- **Internas**: Toda implementación de dominio

## Estimación en horas
3 horas