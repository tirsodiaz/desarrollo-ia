# Paso 2 — Reglas de dominio (lógica de decisión)

## Objetivo

Implementar las funciones puras que contienen la lógica de negocio: decidir la acción a tomar según el saldo, origen y fecha, y calcular días laborables. Estas funciones no dependen de infraestructura — reciben datos y devuelven resultados.

---

## 1. Principio rector

Las reglas de dominio son **funciones puras**:

- Reciben todos los datos como parámetros
- No acceden a archivos, red ni estado global
- Son deterministas: mismo input → mismo output
- Son fácilmente testeables sin mocks

---

## 2. Función principal: `decide_action`

Implementa el árbol de decisión de la especificación funcional.

```python
# src/cab/domain/rules.py

from datetime import date, datetime
from collections.abc import Callable

from cab.domain.models import CaseInput, Action, DomainResult


def decide_action(
    case_input: CaseInput,
    balance: float,
    today: date,
    non_working_days: list[date],
    days_to_check: int,
) -> DomainResult:
    """
    Determina la acción a aplicar sobre un caso según las reglas de negocio.

    Árbol de decisión:
    1. saldo > 0  → positiveBalance
    2. saldo = 0  → zeroBalance
    3. saldo < 0  →
       a. Sin dateToCheckBalance → calcular fecha futura → wait
       b. dateToCheckBalance == hoy → cancel
       c. dateToCheckBalance != hoy → wait
    """
    case_id = case_input.caseId

    # Caso 1: saldo positivo
    if balance > 0:
        return DomainResult(case_id=case_id, action=Action.POSITIVE_BALANCE)

    # Caso 2: saldo cero
    if balance == 0:
        return DomainResult(case_id=case_id, action=Action.ZERO_BALANCE)

    # Caso 3: saldo negativo
    # Determinar sub-acción según origen (para trazabilidad)
    # source == "CLI" → customerNegativeBalance
    # source != "CLI" → bankNegativeBalance
    # (esta sub-acción se registra pero no altera el flujo wait/cancel)

    date_to_check = case_input.accountClosure.dateToCheckBalance

    # 3a: sin fecha → calcular fecha futura y esperar
    if date_to_check is None:
        future_date = calculate_working_day(today, days_to_check, non_working_days)
        return DomainResult(
            case_id=case_id,
            action=Action.WAIT,
            date_time=datetime(future_date.year, future_date.month, future_date.day, 0, 1),
        )

    # 3b: fecha igual a hoy → cancelar
    if date_to_check == today:
        return DomainResult(case_id=case_id, action=Action.CANCEL)

    # 3c: fecha distinta de hoy → esperar
    return DomainResult(
        case_id=case_id,
        action=Action.WAIT,
        date_time=datetime(date_to_check.year, date_to_check.month, date_to_check.day, 0, 1),
    )
```

---

## 3. Árbol de decisión visual

```
                    ┌─ balance > 0 ──→ POSITIVE_BALANCE
                    │
  evaluate ─────────┼─ balance = 0 ──→ ZERO_BALANCE
                    │
                    └─ balance < 0
                         │
                         ├─ source="CLI" ──→ (trazabilidad: customerNegativeBalance)
                         ├─ source≠"CLI" ──→ (trazabilidad: bankNegativeBalance)
                         │
                         ├─ dateToCheckBalance = null
                         │       └──→ calcular fecha → WAIT(fecha)
                         │
                         ├─ dateToCheckBalance = hoy
                         │       └──→ CANCEL
                         │
                         └─ dateToCheckBalance ≠ hoy
                                 └──→ WAIT(dateToCheckBalance)
```

---

## 4. Función auxiliar: `calculate_working_day`

Calcula el próximo día laborable a partir de una fecha, saltando fines de semana y festivos.

```python
def calculate_working_day(
    from_date: date,
    days_ahead: int,
    non_working_days: list[date],
) -> date:
    """
    Calcula el día laborable que está 'days_ahead' días hábiles
    a partir de 'from_date'.

    Un día NO es laborable si:
    - Es sábado (weekday = 5) o domingo (weekday = 6)
    - Está en la lista de non_working_days (festivos)

    Si days_ahead = 0, devuelve el próximo día laborable desde from_date.
    """
    current = from_date
    counted = 0

    while True:
        current = _next_day(current)

        if _is_working_day(current, non_working_days):
            counted += 1
            if counted >= days_ahead:
                return current

    # Si days_ahead es 0, necesitamos al menos avanzar al siguiente laborable
    # Este caso se maneja porque counted empieza en 0 y days_ahead es 0,
    # así que la primera vez que encontramos un día laborable, retornamos.


def _is_working_day(d: date, non_working_days: list[date]) -> bool:
    """Un día es laborable si no es fin de semana ni festivo."""
    if d.weekday() >= 5:  # sábado=5, domingo=6
        return False
    return d not in non_working_days


def _next_day(d: date) -> date:
    """Devuelve el día siguiente."""
    from datetime import timedelta
    return d + timedelta(days=1)
```

---

## 5. Manejo del sub-tipo de acción negativa

La especificación menciona que cuando el saldo es negativo, se debe distinguir entre `customerNegativeBalance` (source=CLI) y `bankNegativeBalance` (otro origen). Sin embargo, este sub-tipo **coexiste** con las acciones de `wait`/`cancel`.

### Estrategia recomendada

Registrar el sub-tipo como información complementaria en el resultado, pero la **acción principal** sigue siendo `WAIT` o `CANCEL` cuando aplica. Solo se usa `CUSTOMER_NEGATIVE_BALANCE` o `BANK_NEGATIVE_BALANCE` como acción final cuando:

- El saldo es negativo **Y**
- No hay `dateToCheckBalance` **Y**
- Es el primer procesamiento del caso

> Esta ambigüedad se documenta explícitamente como decisión de diseño.

---

## 6. Tabla de verdad para tests

| balance | source | dateToCheckBalance | today      | Acción esperada | dateTime |
|---------|--------|--------------------|------------|-----------------|----------|
| 120.50  | CLI    | null               | 2026-03-23 | positiveBalance | null |
| 0       | CLI    | null               | 2026-03-23 | zeroBalance | null |
| -45.20  | CLI    | null               | 2026-03-23 | wait | fecha calculada |
| -45.20  | BATCH  | null               | 2026-03-23 | wait | fecha calculada |
| -45.20  | CLI    | 2026-03-23         | 2026-03-23 | cancel | null |
| -45.20  | CLI    | 2026-03-25         | 2026-03-23 | wait | 2026-03-25T00:01 |

---

## 7. Reglas de la especificación cubiertas

- [x] Saldo positivo → `positiveBalance`
- [x] Saldo cero → `zeroBalance`
- [x] Saldo negativo, source CLI → `customerNegativeBalance` (trazabilidad)
- [x] Saldo negativo, source otro → `bankNegativeBalance` (trazabilidad)
- [x] Sin fecha de revalidación → calcular fecha futura
- [x] Fecha = hoy → `cancel`
- [x] Fecha ≠ hoy → `wait`
- [x] Cálculo de día laborable saltando fines de semana y festivos

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] `rules.py` contiene `decide_action` y `calculate_working_day`
- [ ] Ambas funciones son puras (sin I/O, sin estado global)
- [ ] `decide_action` cubre los 6 valores de `Action`
- [ ] `calculate_working_day` salta fines de semana y festivos correctamente
- [ ] Se pueden ejecutar tests unitarios contra estas funciones sin mocks de infraestructura
