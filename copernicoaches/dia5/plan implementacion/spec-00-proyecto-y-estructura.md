# Paso 0 — Configuración del proyecto y estructura de carpetas

## Objetivo

Inicializar el proyecto Python con su configuración, dependencias y la estructura de directorios que refleja la arquitectura hexagonal.

---

## 1. Crear el proyecto

Usar `pyproject.toml` como descriptor del proyecto.

```toml
[project]
name = "check-account-balance"
version = "0.1.0"
description = "Simulación de proceso automático de verificación de saldo"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "typer>=0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov",
]

[project.scripts]
cab = "cab.cli.commands:app"
```

---

## 2. Estructura de directorios del código

La arquitectura hexagonal separa el sistema en tres capas concéntricas: dominio (centro), aplicación (orquestación) e infraestructura (adaptadores externos).

```
src/
└── cab/                          ← paquete raíz
    ├── __init__.py
    │
    ├── domain/                   ← CAPA INTERIOR: modelos y reglas puras
    │   ├── __init__.py
    │   ├── models.py             → entidades, value objects, enums
    │   └── rules.py              → funciones puras de decisión
    │
    ├── application/              ← CAPA INTERMEDIA: orquestación y puertos
    │   ├── __init__.py
    │   ├── ports.py              → interfaces (Protocols) de dependencias
    │   ├── processor.py          → caso de uso: procesar un caso
    │   └── service.py            → servicio de procesamiento de archivos
    │
    ├── infrastructure/           ← CAPA EXTERIOR: adaptadores concretos
    │   ├── __init__.py
    │   └── filesystem/
    │       ├── __init__.py
    │       ├── config_readers.py → lectores de configuración (JSON)
    │       └── writers.py        → escritores de resultados
    │
    └── cli/                      ← ADAPTADOR DE ENTRADA
        ├── __init__.py
        └── commands.py           → punto de entrada CLI (Typer)
```

---

## 3. Estructura de carpetas de datos

Crear la estructura de carpetas operativa que el sistema usa en tiempo de ejecución:

```
data/
├── inbox/          → casos pendientes de procesar
├── processing/     → casos en curso
├── outbox/         → resultados correctos
├── errors/         → resultados con error
└── config/         → datos de configuración y simulación
    ├── balances.json
    ├── calendar.json
    └── rules.json
```

---

## 4. Archivos de configuración iniciales

### `data/config/balances.json`

```json
{
  "ACC_001": 120.50,
  "ACC_002": 0,
  "ACC_003": -45.20
}
```

### `data/config/calendar.json`

```json
{
  "non_working_days": ["2026-03-28", "2026-03-29", "2026-04-02"]
}
```

### `data/config/rules.json`

```json
{
  "daysToCheckBalance": 3
}
```

---

## 5. Principios de la arquitectura hexagonal aplicados

| Principio | Aplicación en este proyecto |
|---|---|
| **Dominio independiente** | `domain/` no importa nada de `application/` ni `infrastructure/` |
| **Puertos como contratos** | `application/ports.py` define interfaces que la infraestructura implementa |
| **Adaptadores intercambiables** | Los lectores de archivos podrían sustituirse por APIs sin tocar el dominio |
| **Flujo de dependencias hacia dentro** | CLI → Application → Domain; Infrastructure implementa Ports |
| **Inyección de dependencias** | El procesador recibe sus dependencias como parámetros |

---

## 6. Diagrama de dependencias

```
┌─────────────────────────────────────────────┐
│              CLI (commands.py)               │  ← adaptador de entrada
│  Construye dependencias, lanza el servicio  │
└──────────────────┬──────────────────────────┘
                   │ usa
┌──────────────────▼──────────────────────────┐
│         APPLICATION (service.py)            │  ← orquestación
│  FileProcessingService                      │
│  ├── usa processor.py (caso de uso)         │
│  └── usa ports.py (interfaces)              │
└──────┬───────────────────┬──────────────────┘
       │ implementa        │ usa
┌──────▼───────┐   ┌───────▼──────────────────┐
│INFRASTRUCTURE│   │       DOMAIN             │  ← lógica pura
│ (adaptadores)│   │  models.py + rules.py    │
│ filesystem/  │   │  Sin dependencias externas│
└──────────────┘   └──────────────────────────┘
```

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] Existe `pyproject.toml` con las dependencias definidas
- [ ] La estructura de directorios `src/cab/` está creada con `__init__.py` en cada paquete
- [ ] La estructura `data/` existe con los archivos de configuración
- [ ] Se puede ejecutar `pip install -e .` sin errores
