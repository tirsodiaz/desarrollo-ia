# SPEC01-SETUP-TOOLCHAIN-Instalar y configurar uv

## Descripción técnica detallada
Instalar uv como gestor de dependencias y entornos virtuales, configurarlo para el proyecto `docconv` y verificar su funcionamiento correcto. Uv debe reemplazar completamente pip para todas las operaciones de dependencias.

## Objetivo arquitectónico
Implementar el toolchain obligatorio definido en la guía de arquitectura (sección 6.1), asegurando que todas las operaciones de dependencias y ejecución se realicen a través de uv para mantener consistencia y reproducibilidad.

## Criterios de aceptación
- uv instalado y disponible en PATH
- `uv sync` crea entorno virtual correctamente
- `uv run python --version` funciona
- No se usa pip directamente en el proyecto
- Entorno virtual activado automáticamente por uv

## Artefactos o entregables
- uv instalado en el sistema
- Comando `uv sync` ejecutable sin errores
- Documentación de comandos uv en README

## Dependencias externas e internas
- **Externas**: Acceso a internet para instalación de uv
- **Internas**: pyproject.toml configurado

## Estimación en horas
1 hora