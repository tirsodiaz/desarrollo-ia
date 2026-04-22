# SPEC01-SETUP-QUALITY-Configurar pytest y ruff

## Descripción técnica detallada
Configurar pytest para testing con cobertura ≥90% y ruff para linting y formatting, integrándolos en pyproject.toml y verificando su funcionamiento en el pipeline de validación.

## Objetivo arquitectónico
Implementar los estándares de calidad de código obligatorios (sección 6.4 y 6.5 de guía), asegurando que el proyecto tenga testing exhaustivo y código formateado consistentemente desde el inicio.

## Criterios de aceptación
- pytest configurado con cobertura en pyproject.toml
- ruff configurado para linting y formatting
- Comando `uv run pytest --collect-only` funciona
- Comando `uv run ruff check .` ejecutable
- Comando `uv run ruff format .` operativo
- Cobertura objetivo ≥90% configurada

## Artefactos o entregables
- Configuración pytest en pyproject.toml
- Configuración ruff en pyproject.toml
- Scripts de validación ejecutables
- ADR sobre estándares de calidad adoptados

## Dependencias externas e internas
- **Externas**: pytest y ruff instalables vía uv
- **Internas**: pyproject.toml y estructura de directorios

## Estimación en horas
1.5 horas