# Paso 7 — Adaptador de entrada: CLI

## Objetivo

Implementar el punto de entrada del sistema — un comando de consola que construye todas las dependencias, las conecta y lanza el procesamiento. Este es el **Composition Root** de la arquitectura hexagonal.

---

## 1. Qué es el Composition Root

En arquitectura hexagonal, el **Composition Root** es el único lugar donde se crean las instancias concretas y se inyectan las dependencias. Todo el resto del código trabaja con interfaces (puertos).

```
  CLI (Composition Root)
    │
    ├── crea FileBalanceProvider(config_dir)
    ├── crea FileCalendarProvider(config_dir)
    ├── crea FileRulesProvider(config_dir)
    ├── crea CheckAccountBalanceProcessor(providers...)
    ├── crea OutputWriter(outbox_dir)
    ├── crea ErrorWriter(errors_dir)
    ├── crea FileProcessingService(dirs, processor, writers)
    │
    └── lanza service.process_all()
```

---

## 2. Implementación

```python
# src/cab/cli/commands.py

import logging
from pathlib import Path

import typer

from cab.application.processor import CheckAccountBalanceProcessor
from cab.application.service import FileProcessingService
from cab.infrastructure.filesystem.config_readers import (
    FileBalanceProvider,
    FileCalendarProvider,
    FileRulesProvider,
)
from cab.infrastructure.filesystem.writers import OutputWriter, ErrorWriter

app = typer.Typer(help="Check Account Balance — Verificación automática de saldo")


@app.command()
def run(
    data_dir: Path = typer.Option(
        Path("data"),
        "--data-dir",
        "-d",
        help="Directorio raíz de datos (contiene inbox/, outbox/, etc.)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Activar logging detallado",
    ),
) -> None:
    """Procesa todos los casos pendientes en inbox/."""

    # Configurar logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    # Resolver directorios
    inbox_dir = data_dir / "inbox"
    processing_dir = data_dir / "processing"
    outbox_dir = data_dir / "outbox"
    errors_dir = data_dir / "errors"
    config_dir = data_dir / "config"

    # Verificar que existen
    for d in [inbox_dir, processing_dir, outbox_dir, errors_dir, config_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Construir dependencias (Composition Root)
    balance_provider = FileBalanceProvider(config_dir)
    calendar_provider = FileCalendarProvider(config_dir)
    rules_provider = FileRulesProvider(config_dir)

    processor = CheckAccountBalanceProcessor(
        balance_provider=balance_provider,
        calendar_provider=calendar_provider,
        rules_provider=rules_provider,
    )

    output_writer = OutputWriter(outbox_dir)
    error_writer = ErrorWriter(errors_dir)

    service = FileProcessingService(
        inbox_dir=inbox_dir,
        processing_dir=processing_dir,
        processor=processor,
        output_writer=output_writer,
        error_writer=error_writer,
    )

    # Ejecutar
    count = service.process_all()

    if count == 0:
        typer.echo("No hay casos pendientes en inbox/")
    else:
        typer.echo(f"Procesados {count} caso(s)")


if __name__ == "__main__":
    app()
```

---

## 3. Uso desde la línea de comandos

```bash
# Procesar con la carpeta de datos por defecto (./data/)
cab run

# Especificar otra carpeta de datos
cab run --data-dir /ruta/a/mis/datos

# Con logging detallado
cab run --verbose

# Ayuda
cab --help
```

---

## 4. Diagrama de ensamblaje

```
┌─────────────────────────────────────────────────────┐
│                  CLI (commands.py)                   │
│                                                     │
│  data_dir ──→ config_dir ──→ FileBalanceProvider    │
│                           ──→ FileCalendarProvider  │
│                           ──→ FileRulesProvider     │
│                                     │               │
│                                     ▼               │
│           CheckAccountBalanceProcessor              │
│                      │                              │
│  data_dir ──→ outbox_dir ──→ OutputWriter           │
│           ──→ errors_dir ──→ ErrorWriter            │
│                      │                              │
│                      ▼                              │
│           FileProcessingService                     │
│           ├── inbox_dir                             │
│           ├── processing_dir                        │
│           ├── processor                             │
│           ├── output_writer                         │
│           └── error_writer                          │
│                      │                              │
│                      ▼                              │
│              service.process_all()                  │
└─────────────────────────────────────────────────────┘
```

---

## 5. Decisiones de diseño

| Decisión | Justificación |
|---|---|
| `typer` como framework CLI | Simple, tipado, genera ayuda automática |
| `data_dir` como parámetro configurable | Permite ejecutar con diferentes conjuntos de datos |
| `mkdir(parents=True, exist_ok=True)` | Crea las carpetas si no existen, evita errores |
| Logging configurable con `--verbose` | Facilita depuración sin ensuciar la salida normal |
| No hay lógica de negocio en el CLI | Solo construye dependencias y lanza |

---

## 6. Registro como script en `pyproject.toml`

```toml
[project.scripts]
cab = "cab.cli.commands:app"
```

Tras `pip install -e .`, el comando `cab` estará disponible globalmente.

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] `commands.py` define un comando `run` con Typer
- [ ] El CLI construye todas las dependencias y lanza el servicio
- [ ] Se puede ejecutar `cab run` desde la terminal
- [ ] La carpeta de datos es configurable con `--data-dir`
- [ ] Las carpetas se crean automáticamente si no existen
- [ ] El CLI no contiene lógica de negocio
