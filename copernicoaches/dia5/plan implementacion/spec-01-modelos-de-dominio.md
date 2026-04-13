# Paso 1 — Modelos de dominio

## Objetivo

Definir las entidades, value objects y enumeraciones que representan los conceptos del negocio. Estos modelos son el centro de la arquitectura hexagonal: no dependen de nada externo.

---

## 1. Principio rector

Los modelos de dominio:

- Son **inmutables** (value objects) o tienen identidad clara (entidades)
- No importan módulos de infraestructura ni de aplicación
- Usan **Pydantic** para validación declarativa
- Representan exactamente los conceptos de la especificación funcional

---

## 2. Modelo de entrada: `CaseInput`

Representa un caso tal como llega desde el archivo JSON en `/inbox/`.

```python
# src/cab/domain/models.py

from pydantic import BaseModel
from datetime import date
from enum import Enum


class ContractItem(BaseModel):
    """Un contrato/cuenta asociada al caso."""
    contractId: str


class AccountClosure(BaseModel):
    """Datos de cierre de cuenta."""
    dateToCheckBalance: date | None = None
    entity: str = ""


class CaseInput(BaseModel):
    """Caso de entrada para verificación de saldo."""
    caseId: str
    source: str
    contracts: list[ContractItem]
    accountClosure: AccountClosure = AccountClosure()
```

### Decisiones de diseño

| Decisión | Justificación |
|---|---|
| `dateToCheckBalance` es `date \| None` | La especificación indica que puede no existir |
| `contracts` es una lista | El caso puede tener múltiples contratos; se usa `contracts[0]` |
| `entity` tiene valor por defecto `""` | Campo opcional en algunos casos |
| Se usa `BaseModel` de Pydantic | Validación automática y serialización |

---

## 3. Value Object: `BalanceData`

Encapsula el saldo obtenido para una cuenta.

```python
class BalanceData(BaseModel):
    """Saldo de una cuenta."""
    account_id: str
    amount: float

    model_config = {"frozen": True}
```

> `frozen=True` hace el modelo inmutable, como corresponde a un value object.

---

## 4. Enumeración: `Action`

Las posibles acciones resultado del proceso de decisión.

```python
class Action(str, Enum):
    """Acciones posibles resultado de la verificación de saldo."""
    POSITIVE_BALANCE = "positiveBalance"
    ZERO_BALANCE = "zeroBalance"
    CUSTOMER_NEGATIVE_BALANCE = "customerNegativeBalance"
    BANK_NEGATIVE_BALANCE = "bankNegativeBalance"
    WAIT = "wait"
    CANCEL = "cancel"
```

### Mapeo con la especificación

| Condición | Acción |
|---|---|
| saldo > 0 | `POSITIVE_BALANCE` |
| saldo = 0 | `ZERO_BALANCE` |
| saldo < 0, source = "CLI" | `CUSTOMER_NEGATIVE_BALANCE` |
| saldo < 0, source ≠ "CLI" | `BANK_NEGATIVE_BALANCE` |
| saldo < 0, fecha = hoy | `CANCEL` |
| saldo < 0, fecha ≠ hoy o sin fecha | `WAIT` |

---

## 5. Modelo de resultado: `DomainResult`

El resultado de procesar un caso.

```python
from datetime import datetime


class DomainResult(BaseModel):
    """Resultado del procesamiento de un caso."""
    case_id: str
    action: Action
    date_time: datetime | None = None

    model_config = {"frozen": True}
```

---

## 6. Modelos de salida: payloads serializables

Para generar los archivos JSON de salida.

```python
class OutputPayload(BaseModel):
    """Payload de salida exitosa para /outbox/."""
    caseId: str
    action: str
    dateTime: str | None = None


class ErrorEntry(BaseModel):
    """Una entrada individual de error."""
    code: str
    message: str


class ErrorPayload(BaseModel):
    """Payload de error para /errors/."""
    caseId: str
    taskName: str = "Check Account Balance"
    dateTime: str
    errors: list[ErrorEntry]
```

---

## 7. Relación entre modelos

```
CaseInput ──────────────┐
  ├── ContractItem[]     │
  └── AccountClosure     │   → reglas de decisión →   DomainResult
                         │                               ├── Action (enum)
BalanceData ─────────────┘                               └── date_time?
                                                              │
                                                              ▼
                                                     OutputPayload
                                                         o
                                                     ErrorPayload
```

---

## 8. Archivo completo

El archivo `src/cab/domain/models.py` debe contener todas las clases anteriores en un único módulo, ordenadas de menor a mayor dependencia.

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] `models.py` define `ContractItem`, `AccountClosure`, `CaseInput`, `BalanceData`, `Action`, `DomainResult`, `OutputPayload`, `ErrorEntry`, `ErrorPayload`
- [ ] Ningún modelo importa módulos de `application/` ni `infrastructure/`
- [ ] Se puede instanciar `CaseInput` con un JSON válido de ejemplo
- [ ] `Action` tiene exactamente los 6 valores de la especificación
- [ ] Los modelos inmutables usan `frozen=True`
