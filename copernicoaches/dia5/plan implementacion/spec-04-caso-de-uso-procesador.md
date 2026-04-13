# Paso 4 — Caso de uso: procesador de verificación de saldo

## Objetivo

Implementar el caso de uso principal que orquesta la lógica de dominio con los puertos. Este procesador es la pieza central de la capa de aplicación: recibe un caso de entrada, consulta los datos necesarios a través de los puertos, invoca las reglas de dominio y devuelve el resultado.

---

## 1. Rol en la arquitectura hexagonal

```
  CLI (entrada)
       │
       ▼
  Service (orquestación de archivos)     ← paso 6
       │
       ▼
  ┌─────────────────────────────────┐
  │ CheckAccountBalanceProcessor    │    ← ESTE PASO
  │                                 │
  │  1. Extrae accountId            │
  │  2. Consulta saldo (puerto)     │
  │  3. Consulta calendario (puerto)│
  │  4. Consulta reglas (puerto)    │
  │  5. Llama a decide_action()     │
  │  6. Devuelve DomainResult       │
  └─────────────────────────────────┘
       │                    │
       ▼                    ▼
    domain/rules.py    application/ports.py
```

El procesador **no sabe** de dónde vienen los datos. Solo usa las interfaces (puertos).

---

## 2. Implementación

```python
# src/cab/application/processor.py

from datetime import date

from cab.domain.models import CaseInput, DomainResult
from cab.domain.rules import decide_action
from cab.application.ports import (
    BalanceProvider,
    CalendarProvider,
    RulesProvider,
    BalanceNotFoundError,
    ProcessingError,
)


class CheckAccountBalanceProcessor:
    """
    Caso de uso: verificar el saldo de una cuenta y determinar la acción.

    Recibe dependencias por inyección (puertos) y orquesta
    la lógica de dominio.
    """

    def __init__(
        self,
        balance_provider: BalanceProvider,
        calendar_provider: CalendarProvider,
        rules_provider: RulesProvider,
    ) -> None:
        self._balance_provider = balance_provider
        self._calendar_provider = calendar_provider
        self._rules_provider = rules_provider

    def process(self, case_input: CaseInput) -> DomainResult:
        """
        Procesa un caso de verificación de saldo.

        1. Extrae el accountId del primer contrato
        2. Obtiene el saldo de la cuenta
        3. Obtiene días no laborables y parámetros de reglas
        4. Aplica las reglas de decisión
        5. Devuelve el resultado

        Raises:
            ProcessingError: si no se puede procesar (cuenta sin contratos,
                            saldo no encontrado, etc.)
        """
        # 1. Extraer accountId
        account_id = self._extract_account_id(case_input)

        # 2. Obtener saldo
        try:
            balance = self._balance_provider.get_balance(account_id)
        except BalanceNotFoundError as e:
            raise ProcessingError(
                code="ERR001",
                message=f"Balance no encontrado para cuenta: {account_id}",
            ) from e

        # 3. Obtener datos de calendario y reglas
        non_working_days = self._calendar_provider.get_non_working_days()
        days_to_check = self._rules_provider.get_days_to_check_balance()

        # 4. Aplicar reglas de decisión
        today = date.today()
        return decide_action(
            case_input=case_input,
            balance=balance,
            today=today,
            non_working_days=non_working_days,
            days_to_check=days_to_check,
        )

    def _extract_account_id(self, case_input: CaseInput) -> str:
        """Extrae el accountId del primer contrato del caso."""
        if not case_input.contracts:
            raise ProcessingError(
                code="ERR002",
                message=f"Caso {case_input.caseId} sin contratos asociados",
            )

        contract_id = case_input.contracts[0].contractId
        if not contract_id.strip():
            raise ProcessingError(
                code="ERR003",
                message=f"Caso {case_input.caseId} con contractId vacío",
            )

        return contract_id
```

---

## 3. Decisiones de diseño

| Decisión | Justificación |
|---|---|
| Inyección por constructor | Las dependencias se pasan al crear el procesador, no en cada llamada |
| `contracts[0]` como cuenta principal | La especificación indica usar el primer contrato |
| Conversión de `BalanceNotFoundError` a `ProcessingError` | Los errores de dominio se traducen a errores de aplicación con código |
| `date.today()` dentro del procesador | El procesador tiene la responsabilidad de determinar "hoy" |
| Validación de contratos vacíos | Caso límite: un caso podría llegar sin contratos |

---

## 4. Flujo de errores

```
Caso sin contratos ──→ ProcessingError(ERR002)
ContractId vacío   ──→ ProcessingError(ERR003)
Cuenta no existe   ──→ ProcessingError(ERR001)
Error inesperado   ──→ se propaga sin capturar (lo maneja el servicio)
```

Los `ProcessingError` se convierten al final en archivos dentro de `/errors/` con el formato especificado.

---

## 5. Testabilidad

El procesador se puede testear con implementaciones simples de los puertos:

```python
# Ejemplo de test
class MockBalanceProvider:
    def __init__(self, balances: dict[str, float]):
        self._balances = balances

    def get_balance(self, account_id: str) -> float:
        if account_id not in self._balances:
            raise BalanceNotFoundError(account_id)
        return self._balances[account_id]


class MockCalendarProvider:
    def get_non_working_days(self) -> list[date]:
        return []


class MockRulesProvider:
    def get_days_to_check_balance(self) -> int:
        return 3


# No se necesita herencia, mocks ni frameworks — solo duck typing
processor = CheckAccountBalanceProcessor(
    balance_provider=MockBalanceProvider({"ACC_001": 120.50}),
    calendar_provider=MockCalendarProvider(),
    rules_provider=MockRulesProvider(),
)
result = processor.process(case_input)
```

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] `processor.py` define `CheckAccountBalanceProcessor`
- [ ] El procesador recibe los tres puertos por inyección en el constructor
- [ ] El método `process()` extrae la cuenta, consulta el saldo, y llama a `decide_action`
- [ ] Los errores se traducen a `ProcessingError` con códigos explícitos
- [ ] Se puede instanciar y testear el procesador con mocks simples sin infraestructura
