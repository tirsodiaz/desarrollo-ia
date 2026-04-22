# SPEC05-ADAPTERS-CLI-Implementar adaptador CLI

## Descripción técnica detallada
Desarrollar el adaptador de línea de comandos que parsea argumentos `input.docx output.md`, llama a `convert_file()` y muestra resultados por stdout/stderr.

## Objetivo arquitectónico
Implementar interfaz CLI ligera que no contiene lógica de negocio, siguiendo principios de adaptadores y separación de concerns.

## Criterios de aceptación
- Módulo `cli/adapter.py` con función `run_cli()`
- Parseo correcto de argumentos posicionales
- Salida de resultados por stdout
- Advertencias por stderr
- Código de salida 1 en errores

## Artefactos o entregables
- Adaptador CLI implementado
- Tests unitarios para CLI
- Documentación de uso CLI

## Dependencias externas e internas
- **Externas**: argparse o similar
- **Internas**: Capa de aplicación

## Estimación en horas
2 horas