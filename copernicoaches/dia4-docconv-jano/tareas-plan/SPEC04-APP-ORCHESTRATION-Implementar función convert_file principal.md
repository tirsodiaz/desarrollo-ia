# SPEC04-APP-ORCHESTRATION-Implementar función convert_file principal

## Descripción técnica detallada
Desarrollar la función `convert_file(input_path, output_path)` que orquesta todo el proceso: determinar dirección, leer archivo, convertir, escribir resultado, manejar errores y advertencias.

## Objetivo arquitectónico
Crear el punto de entrada único para la lógica de aplicación, coordinando dominio e infraestructura según principios de capas.

## Criterios de aceptación
- Función `convert_file()` en `application/convert.py`
- Determinación automática de dirección por extensión
- Integración completa dominio + infraestructura
- Retorno de `ConversionResult` con éxito/warnings/error
- Manejo robusto de errores

## Artefactos o entregables
- Función de orquestación implementada
- Modelo `ConversionResult` definido
- Tests de integración para flujo completo

## Dependencias externas e internas
- **Externas**: Ninguna
- **Internas**: Capas dominio e infraestructura completas

## Estimación en horas
3 horas