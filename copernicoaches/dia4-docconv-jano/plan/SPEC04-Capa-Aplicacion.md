# SPEC04 - Implementación de la Capa de Aplicación

## Objetivo

Desarrollar la capa de aplicación que orquesta el proceso completo de conversión, coordinando las capas de dominio e infraestructura para proporcionar la funcionalidad central del sistema.

## Descripción

La capa de aplicación actúa como coordinador principal, recibiendo solicitudes de conversión y delegando tareas a las capas inferiores. Esta capa implementa el caso de uso principal (`convert_file`) que combina lectura de archivos, conversión de dominio y escritura de resultados, manejando errores y generando advertencias según los requerimientos funcionales.

## Tareas principales

- Implementar función principal `convert_file()` que orqueste todo el proceso
- Integrar llamadas a infraestructura (lectura/escritura) con dominio (conversión)
- Implementar determinación automática de dirección de conversión por extensión de archivo
- Gestionar colección y reporte de advertencias desde dominio
- Manejar errores de conversión con códigos de salida apropiados
- Crear modelo de resultado de conversión (`ConversionResult`)
- Implementar validación de parámetros de entrada
- Desarrollar tests de integración para el flujo completo

## Dependencias

- SPEC02 y SPEC03 completados (capas de dominio e infraestructura operativas)
- Especificación funcional v2 (sección 7.1 - Arquitectura recomendada, capa de aplicación)
- Guía de arquitectura (sección 3 - Capas obligatorias, aplicación layer)

## Riesgos y mitigaciones

- **Riesgo**: Coordinación entre capas puede introducir complejidad innecesaria.
  - **Mitigación**: Mantener interfaz simple y clara entre capas, con contratos bien definidos.

- **Riesgo**: Manejo de errores inconsistente entre capas.
  - **Mitigación**: Definir política de errores unificada y tests que validen propagación correcta.

- **Riesgo**: Rendimiento degradado por llamadas innecesarias entre capas.
  - **Mitigación**: Optimizar flujo de datos y evitar conversiones intermedias innecesarias.

## Resultado/Entregable esperado

- Módulo `src/docconv/application/` implementado con `convert_file()` funcional
- Integración completa entre dominio e infraestructura
- Tests de integración pasando para flujo de conversión completo
- Manejo robusto de errores y advertencias
- Determinación automática de dirección de conversión
- Modelo de datos para resultados de conversión