# SPEC-00 | INFRA | SETUP | Crear pyproject.toml y estructura de directorios

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-00-infra-setup-crear-pyproject-y-estructura |
| **CÃ³digo de plan** | SPEC-00 |
| **Ã‰pica** | INFRA â€” ConfiguraciÃ³n del proyecto y estructura |
| **Feature** | SETUP â€” InicializaciÃ³n del proyecto |
| **Tipo** | Tarea tÃ©cnica |
| **Prioridad** | CrÃ­tica |
| **EstimaciÃ³n** | 2 h |

---

## DescripciÃ³n tÃ©cnica

Crear el descriptor del proyecto `pyproject.toml` con dependencias runtime y de desarrollo, y la estructura completa de directorios que refleja la arquitectura de cuatro capas: `state/`, `navigation/`, `filesystem/` y `ui/`.

```toml
[project]
name = "miller-columns"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["rich>=13.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov"]

[project.scripts]
miller = "miller.__main__:main"
```

Estructura a crear bajo `explorer/src/miller/`:

```
src/miller/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ __main__.py          â† punto de entrada mÃ­nimo (mensaje de arranque)
â”œâ”€â”€ state/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ model.py         â† placeholder
â”œâ”€â”€ navigation/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ navigator.py     â† placeholder
â”œâ”€â”€ filesystem/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ reader.py        â† placeholder
â””â”€â”€ ui/
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ renderer.py      â† placeholder
    â””â”€â”€ input_handler.py â† placeholder
tests/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ test_model.py
â”œâ”€â”€ test_navigator.py
â”œâ”€â”€ test_reader.py
â””â”€â”€ test_renderer.py
```

---

## Objetivo arquitectÃ³nico

Establecer la base estructural que refleja la separaciÃ³n en cuatro capas desacopladas. La estructura de carpetas es la primera expresiÃ³n de las decisiones arquitectÃ³nicas: cualquier desarrollador debe poder inferir las responsabilidades solo leyendo los nombres de mÃ³dulos.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | `pyproject.toml` con `name`, `requires-python`, dependencia `rich>=13.0`, extras `dev`, script `miller` |
| CA-2 | Toda la estructura de carpetas existe con `__init__.py` en cada paquete |
| CA-3 | `pip install -e .` finaliza sin errores |
| CA-4 | `python -m miller` imprime mensaje de arranque sin traceback |
| CA-5 | `pytest` ejecuta sin errores (0 tests, 0 fallos) |

---

## Artefactos y entregables

- `pyproject.toml` configurado
- Ãrbol de directorios completo
- `__main__.py` con funciÃ³n `main()` mÃ­nima funcional
- Archivos placeholder en cada capa

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | Ninguna â€” es el paso cero de inicializaciÃ³n |
| **Externa** | Python >= 3.12 instalado en el entorno |
| **Bloquea** | SPEC-00-INFRA-ADR, SPEC-00-INFRA-VERIFICACION y todos los pasos siguientes |


