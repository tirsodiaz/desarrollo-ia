# SPEC01 - Configuración del Proyecto y Toolchain

## Objetivo

Establecer la estructura base del proyecto `docconv` siguiendo los estándares arquitectónicos definidos, configurando el toolchain recomendado (Python + uv) y preparando el entorno de desarrollo para la implementación de la aplicación de conversión de documentos.

## Descripción

Este paso inicial configura la infraestructura técnica del proyecto, asegurando que se cumplan los principios de arquitectura en capas y los estándares de calidad definidos en la guía de arquitectura. Se establece el entorno de desarrollo con herramientas como `uv`, `pytest` y `ruff`, y se crea la estructura de directorios base que soportará las capas de dominio, aplicación e infraestructura.

## Tareas principales

- Configurar `pyproject.toml` como fuente única de verdad para dependencias, herramientas y configuración
- Instalar y configurar `uv` para gestión de dependencias y ejecución
- Crear estructura de directorios según la guía de arquitectura:
  - `src/docconv/` con subdirectorios para capas
  - `tests/` con subdirectorios para tipos de pruebas
- Configurar `pytest` para testing con cobertura ≥90%
- Configurar `ruff` para linting y formatting
- Crear archivos base (`__main__.py`, `main.py`) para punto de entrada
- Verificar compatibilidad con Python 3.11+

## Dependencias

- Ninguna (paso inicial)
- Acceso a la guía de arquitectura (`Architecture-Guide.md`)
- Especificación funcional v2 para validar alcance inicial

## Riesgos y mitigaciones

- **Riesgo**: Configuración incorrecta de `uv` o `pyproject.toml` puede causar problemas de dependencias.
  - **Mitigación**: Seguir exactamente la sección 6.1 de la guía de arquitectura y validar con `uv sync`.

- **Riesgo**: Estructura de directorios no alineada con arquitectura en capas.
  - **Mitigación**: Revisar contra la sección 6.2 de la guía antes de proceder al siguiente paso.

- **Riesgo**: Versiones incompatibles de herramientas.
  - **Mitigación**: Usar versiones específicas recomendadas en la guía de arquitectura.

## Resultado/Entregable esperado

- Proyecto `docconv` configurado en `C:\cursos\desarrollo-ia\copernicoaches\docconv` con estructura completa
- `pyproject.toml` funcional con todas las dependencias y herramientas configuradas
- Comando `uv run python -m docconv --help` retorna información básica (aunque funcionalidad aún no implementada)
- Pipeline de validación básico ejecutable: `uv sync && uv run ruff check . && uv run pytest --collect-only`
- Documentación del setup en `README.md` del proyecto