# Paso 3 — Puertos de aplicación (interfaces)

## Objetivo

Definir los **puertos** (interfaces) que la capa de aplicación necesita para acceder a datos externos. Estos puertos son el mecanismo central de la arquitectura hexagonal: permiten que el dominio y la aplicación no dependan de detalles de infraestructura.

---

## 1. Qué es un puerto en arquitectura hexagonal

Un **puerto** es una interfaz que define *qué necesita* la aplicación, sin especificar *cómo se obtiene*. Los puertos se implementan mediante **adaptadores** en la capa de infraestructura.

```
  Dominio          Aplicación          Infraestructura
  ──────           ──────────          ───────────────
  models.py   ←──  ports.py    ──→    config_readers.py
  rules.py    ←──  processor.py       writers.py
                                      (implementan los puertos)
```

En Python, los puertos se definen como `Protocol` (typing) — duck typing estructural sin necesidad de herencia.

---

## 2. Puerto: `BalanceProvider`

Proporciona el saldo de una cuenta.

```python
# src/cab/application/ports.py

from typing import Protocol
from datetime import date


class BalanceProvider(Protocol):
    """Puerto para obtener el saldo de una cuenta."""

    def get_balance(self, account_id: str) -> float:
        """
        Devuelve el saldo asociado a una cuenta.

        Raises:
            BalanceNotFoundError: si la cuenta no existe en el sistema.
        """
        ...
```

---

## 3. Puerto: `CalendarProvider`

Proporciona la lista de días no laborables.

```python
class CalendarProvider(Protocol):
    """Puerto para obtener información de calendario."""

    def get_non_working_days(self) -> list[date]:
        """Devuelve la lista de días no laborables (festivos)."""
        ...
```

---

## 4. Puerto: `RulesProvider`

Proporciona los parámetros configurables de las reglas de negocio.

```python
class RulesProvider(Protocol):
    """Puerto para obtener parámetros de configuración de reglas."""

    def get_days_to_check_balance(self) -> int:
        """Devuelve el número de días hábiles para calcular fecha de revalidación."""
        ...
```

---

## 5. Excepciones de dominio

Excepciones que forman parte del contrato de los puertos.

```python
class BalanceNotFoundError(Exception):
    """El saldo para la cuenta solicitada no existe."""

    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        super().__init__(f"Balance no encontrado para cuenta: {account_id}")


class ProcessingError(Exception):
    """Error genérico de procesamiento con código y mensaje."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")
```

---

## 6. Mapa de puertos y sus implementaciones futuras

| Puerto | Método | Adaptador (paso 5) |
|---|---|---|
| `BalanceProvider` | `get_balance(account_id)` | `FileBalanceProvider` → lee `balances.json` |
| `CalendarProvider` | `get_non_working_days()` | `FileCalendarProvider` → lee `calendar.json` |
| `RulesProvider` | `get_days_to_check_balance()` | `FileRulesProvider` → lee `rules.json` |

---

## 7. Por qué usar `Protocol` y no `ABC`

| Aspecto | `Protocol` | `ABC` |
|---|---|---|
| Herencia requerida | No | Sí |
| Duck typing | Sí (estructural) | No |
| Facilidad de testing | Alta (cualquier objeto con los métodos correctos vale) | Media (requiere herencia explícita) |
| Pythónico | Más | Menos |

`Protocol` permite que los tests usen simples clases o incluso `MagicMock` sin necesidad de heredar de nada.

---

## 8. Diagrama de flujo de dependencias

```
    ┌──────────────────────┐
    │   ports.py           │   ← define los contratos
    │   BalanceProvider    │
    │   CalendarProvider   │
    │   RulesProvider      │
    └──────┬───────────────┘
           │
     ┌─────┴──────────────────────────────┐
     │                                     │
     ▼                                     ▼
┌────────────────┐              ┌──────────────────────┐
│ processor.py   │              │ infrastructure/      │
│ (usa los       │              │ filesystem/          │
│  puertos)      │              │ config_readers.py    │
│                │              │ (implementa los      │
│                │              │  puertos)            │
└────────────────┘              └──────────────────────┘
```

---

## 9. Archivo completo esperado

```python
# src/cab/application/ports.py

from typing import Protocol
from datetime import date


class BalanceProvider(Protocol):
    def get_balance(self, account_id: str) -> float: ...


class CalendarProvider(Protocol):
    def get_non_working_days(self) -> list[date]: ...


class RulesProvider(Protocol):
    def get_days_to_check_balance(self) -> int: ...


class BalanceNotFoundError(Exception):
    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        super().__init__(f"Balance no encontrado para cuenta: {account_id}")


class ProcessingError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")
```

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] `ports.py` define los tres protocolos: `BalanceProvider`, `CalendarProvider`, `RulesProvider`
- [ ] Las excepciones `BalanceNotFoundError` y `ProcessingError` están definidas
- [ ] Ningún puerto importa módulos de infraestructura
- [ ] Los puertos usan `Protocol` (no `ABC`)
- [ ] Cada método tiene una firma clara con tipos anotados
