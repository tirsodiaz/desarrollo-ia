# Paso 5 — Adaptadores de infraestructura (sistema de archivos)

## Objetivo

Implementar los adaptadores concretos que satisfacen los puertos definidos en el paso 3. Estos adaptadores leen configuración desde archivos JSON y escriben resultados al sistema de archivos.

---

## 1. Rol en la arquitectura hexagonal

Los adaptadores son la capa más externa. Implementan los puertos sin que el dominio ni la aplicación sepan cómo.

```
  application/ports.py              infrastructure/filesystem/
  ─────────────────────             ──────────────────────────
  BalanceProvider       ──→  implementado por  ──→  FileBalanceProvider
  CalendarProvider      ──→  implementado por  ──→  FileCalendarProvider
  RulesProvider         ──→  implementado por  ──→  FileRulesProvider
  (sin puerto formal)   ──→  OutputWriter, ErrorWriter
```

---

## 2. Adaptador: `FileBalanceProvider`

Lee los saldos desde `config/balances.json`.

```python
# src/cab/infrastructure/filesystem/config_readers.py

import json
from pathlib import Path
from datetime import date, datetime

from cab.application.ports import BalanceNotFoundError


class FileBalanceProvider:
    """Lee saldos desde un archivo JSON de configuración."""

    def __init__(self, config_dir: Path) -> None:
        self._path = config_dir / "balances.json"

    def get_balance(self, account_id: str) -> float:
        data = self._load()
        if account_id not in data:
            raise BalanceNotFoundError(account_id)
        return float(data[account_id])

    def _load(self) -> dict:
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)
```

### Formato esperado de `balances.json`

```json
{
  "ACC_001": 120.50,
  "ACC_002": 0,
  "ACC_003": -45.20
}
```

---

## 3. Adaptador: `FileCalendarProvider`

Lee los días no laborables desde `config/calendar.json`.

```python
class FileCalendarProvider:
    """Lee días no laborables desde un archivo JSON de configuración."""

    def __init__(self, config_dir: Path) -> None:
        self._path = config_dir / "calendar.json"

    def get_non_working_days(self) -> list[date]:
        data = self._load()
        return [
            date.fromisoformat(d)
            for d in data.get("non_working_days", [])
        ]

    def _load(self) -> dict:
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)
```

### Formato esperado de `calendar.json`

```json
{
  "non_working_days": ["2026-03-28", "2026-03-29", "2026-04-02"]
}
```

---

## 4. Adaptador: `FileRulesProvider`

Lee parámetros de reglas desde `config/rules.json`.

```python
class FileRulesProvider:
    """Lee parámetros de reglas desde un archivo JSON de configuración."""

    def __init__(self, config_dir: Path) -> None:
        self._path = config_dir / "rules.json"

    def get_days_to_check_balance(self) -> int:
        data = self._load()
        return int(data["daysToCheckBalance"])

    def _load(self) -> dict:
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)
```

### Formato esperado de `rules.json`

```json
{
  "daysToCheckBalance": 3
}
```

---

## 5. Escritor de resultados: `OutputWriter`

Escribe el resultado exitoso en `/outbox/`.

```python
# src/cab/infrastructure/filesystem/writers.py

import json
from pathlib import Path

from cab.domain.models import DomainResult, OutputPayload, ErrorPayload, ErrorEntry


class OutputWriter:
    """Escribe resultados exitosos en la carpeta outbox."""

    def __init__(self, outbox_dir: Path) -> None:
        self._outbox_dir = outbox_dir

    def write(self, result: DomainResult) -> Path:
        payload = OutputPayload(
            caseId=result.case_id,
            action=result.action.value,
            dateTime=result.date_time.isoformat() if result.date_time else None,
        )

        file_path = self._outbox_dir / f"{result.case_id}.json"
        file_path.write_text(
            json.dumps(payload.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return file_path
```

### Ejemplo de salida generada

```json
{
  "caseId": "CASE_001",
  "action": "positiveBalance",
  "dateTime": null
}
```

---

## 6. Escritor de errores: `ErrorWriter`

Escribe errores en `/errors/`.

```python
class ErrorWriter:
    """Escribe errores de procesamiento en la carpeta errors."""

    def __init__(self, errors_dir: Path) -> None:
        self._errors_dir = errors_dir

    def write(self, case_id: str, errors: list[dict]) -> Path:
        payload = ErrorPayload(
            caseId=case_id,
            taskName="Check Account Balance",
            dateTime=datetime.now().isoformat(timespec="seconds"),
            errors=[ErrorEntry(**e) for e in errors],
        )

        file_path = self._errors_dir / f"{case_id}_error.json"
        file_path.write_text(
            json.dumps(payload.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return file_path
```

### Ejemplo de error generado

```json
{
  "caseId": "CASE_001",
  "taskName": "Check Account Balance",
  "dateTime": "2026-03-23T10:00:00",
  "errors": [
    {
      "code": "ERR001",
      "message": "Balance no encontrado para cuenta: ACC_999"
    }
  ]
}
```

---

## 7. Resumen de archivos

| Archivo | Contenido |
|---|---|
| `infrastructure/filesystem/config_readers.py` | `FileBalanceProvider`, `FileCalendarProvider`, `FileRulesProvider` |
| `infrastructure/filesystem/writers.py` | `OutputWriter`, `ErrorWriter` |
| `infrastructure/filesystem/__init__.py` | Vacío |
| `infrastructure/__init__.py` | Vacío |

---

## 8. Diagrama de flujo de datos

```
config/balances.json  ──→  FileBalanceProvider  ──→  processor
config/calendar.json  ──→  FileCalendarProvider ──→  processor
config/rules.json     ──→  FileRulesProvider    ──→  processor

processor ──→ DomainResult ──→ OutputWriter ──→ outbox/{caseId}.json
processor ──→ ProcessingError ──→ ErrorWriter ──→ errors/{caseId}_error.json
```

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] Existen los tres lectores de configuración: `FileBalanceProvider`, `FileCalendarProvider`, `FileRulesProvider`
- [ ] Cada lector satisface su correspondiente protocolo de `ports.py`
- [ ] `OutputWriter` genera JSON con el formato `{caseId, action, dateTime}`
- [ ] `ErrorWriter` genera JSON con el formato `{caseId, taskName, dateTime, errors[]}`
- [ ] Todos los adaptadores reciben sus rutas por constructor (no usan rutas fijas)
- [ ] Se puede verificar con archivos de configuración reales
