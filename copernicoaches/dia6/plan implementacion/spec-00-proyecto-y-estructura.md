# Paso 0 — Configuración del proyecto y estructura de carpetas

## Objetivo

Inicializar el proyecto Python con su configuración, dependencias y la estructura de directorios que refleja la arquitectura de cuatro capas definida en la guía de arquitectura.

---

## 1. Crear el proyecto

Usar `pyproject.toml` como descriptor del proyecto.

```toml
[project]
name = "miller-columns"
version = "0.1.0"
description = "Gestor de archivos en consola con Miller Columns"
requires-python = ">=3.12"
dependencies = [
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov",
]

[project.scripts]
miller = "miller.__main__:main"
```

---

## 2. Estructura de directorios del código

La arquitectura separa el sistema en cuatro capas desacopladas: estado (modelo), lógica de navegación, sistema de archivos y visualización.

```
src/
└── miller/                         ← paquete raíz
    ├── __init__.py
    ├── __main__.py                 → punto de entrada (main)
    │
    ├── state/                      ← CAPA 1: Estado (modelo)
    │   ├── __init__.py
    │   └── model.py                → AppState, FileEntry, enums
    │
    ├── navigation/                 ← CAPA 2: Lógica de navegación
    │   ├── __init__.py
    │   └── navigator.py            → gestión de eventos, transiciones
    │
    ├── filesystem/                 ← CAPA 3: Sistema de archivos
    │   ├── __init__.py
    │   └── reader.py               → lectura de directorios, metadatos, detección de cambios
    │
    └── ui/                         ← CAPA 4: Visualización
        ├── __init__.py
        ├── renderer.py             → renderizado de columnas con Rich
        └── input_handler.py        → captura de teclas
```

---

## 3. Convenciones del proyecto

| Aspecto | Decisión |
|---------|----------|
| Gestión de rutas | `pathlib.Path` exclusivamente |
| Renderizado | `rich` (sin Textual en MVP) |
| Tests | `pytest` con estructura espejo en `tests/` |
| Python mínimo | 3.12+ |

---

## 4. Estructura de tests

```
tests/
├── __init__.py
├── test_model.py          → tests del modelo de estado
├── test_navigator.py      → tests de la lógica de navegación
├── test_reader.py         → tests del lector de filesystem
└── test_renderer.py       → tests del renderizador
```

---

## 5. Inicialización

1. Crear el directorio del proyecto y la estructura de carpetas.
2. Crear `pyproject.toml` con las dependencias.
3. Crear todos los `__init__.py` vacíos.
4. Crear `__main__.py` con un esqueleto mínimo que imprima un mensaje de arranque.
5. Verificar que el proyecto se instala con `pip install -e .` y ejecuta con `python -m miller`.

---

## Criterios de validación de este paso

| # | Verificación |
|---|-------------|
| V1 | La estructura de carpetas existe completa |
| V2 | `pip install -e .` se ejecuta sin errores |
| V3 | `python -m miller` imprime un mensaje de arranque |
| V4 | `pytest` se ejecuta sin errores (0 tests, 0 fallos) |

---

## ✅ Estado de implementación (23–27 de marzo de 2026)

**Completado exitosamente**

- ✅ Estructura de carpetas creada
- ✅ `pyproject.toml` configurado con dependencias (Rich 13.0+, pytest 8.0+)
- ✅ Todos los `__init__.py` creados
- ✅ `__main__.py` implementado con punto de entrada funcional
- ✅ Proyecto instala correctamente: `pip install -e .`
- ✅ Ejecución con: `python -m miller`
- ✅ Cambios de OpenSpec integrados (cambio archivado el 27 de marzo)

**Carpeta destino:** `explorer/src/miller/` en el workspace
