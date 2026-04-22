# SPEC01-SETUP-TOOLCHAIN-Configurar pyproject.toml

## Descripción técnica detallada
Crear el archivo `pyproject.toml` como fuente única de verdad para el proyecto `docconv`, configurando dependencias, herramientas de desarrollo (uv, pytest, ruff), metadatos del proyecto y scripts de ejecución. El archivo debe seguir las mejores prácticas de Python packaging y ser compatible con uv para gestión de dependencias.

## Objetivo arquitectónico
Establecer la configuración central del proyecto que garantice reproducibilidad, calidad de código y consistencia en el toolchain, alineándose con los principios de arquitectura que requieren un solo punto de configuración.

## Criterios de aceptación
- `pyproject.toml` existe en la raíz del proyecto
- Incluye dependencias: python-docx, markdown-it-py, fastmcp, pytest, pytest-cov, ruff
- Configura uv como herramienta principal
- Define scripts para linting, testing y ejecución
- Proyecto se instala correctamente con `uv sync`
- Metadatos del proyecto completos (nombre, versión, autores, descripción)

## Artefactos o entregables
- Archivo `pyproject.toml` funcional
- Validación: `uv sync` ejecuta sin errores
- Documentación de dependencias en comentarios del archivo

## Dependencias externas e internas
- **Externas**: Python 3.11+, acceso a PyPI
- **Internas**: Ninguna (paso inicial)

## Estimación en horas
2 horas