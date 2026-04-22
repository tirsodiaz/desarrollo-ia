# SPEC02-DOMAIN-WARNINGS-Implementar sistema de advertencias

## Descripción técnica detallada
Crear el sistema de advertencias para reportar elementos no soportados o degradados durante la conversión, siguiendo RF-6 de transparencia ante pérdidas.

## Objetivo arquitectónico
Implementar manejo de errores no fatales en la capa de dominio, permitiendo que conversiones continúen mientras informan sobre limitaciones.

## Criterios de aceptación
- Modelo `ConversionWarning` definido
- Advertencias generadas para elementos no soportados (imágenes, HTML)
- Advertencias incluyen tipo de elemento y descripción
- Sistema integrable con capa de aplicación

## Artefactos o entregables
- Clase `ConversionWarning` en models.py
- Lógica de detección de elementos problemáticos
- Tests para generación de advertencias

## Dependencias externas e internas
- **Externas**: Ninguna
- **Internas**: Modelos de datos

## Estimación en horas
2 horas