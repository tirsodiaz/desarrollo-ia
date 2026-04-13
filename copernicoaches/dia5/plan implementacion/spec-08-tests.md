# Paso 8 — Tests

## Objetivo

Implementar los tests que verifican el comportamiento correcto del sistema a todos los niveles: reglas de dominio, procesador, adaptadores y flujo completo. La estrategia de testing refleja la arquitectura hexagonal — cada capa se testea de forma independiente.

---

## 1. Estrategia de testing por capa

```
┌─────────────────────────────────────────────┐
│ Tests de integración (flujo completo)       │  ← pocos, verifican el ensamble
├─────────────────────────────────────────────┤
│ Tests de aplicación (procesador)            │  ← mocks de puertos
├─────────────────────────────────────────────┤
│ Tests de infraestructura (adaptadores)      │  ← archivos temporales
├─────────────────────────────────────────────┤
│ Tests de dominio (reglas puras)             │  ← sin dependencias, más numerosos
└─────────────────────────────────────────────┘
```

---

## 2. Estructura de archivos de test

```
tests/
├── __init__.py
├── conftest.py                    → fixtures compartidos
├── unit/
│   ├── __init__.py
│   ├── test_domain_rules.py       → reglas de decisión y cálculo de fechas
│   ├── test_processor.py          → caso de uso con mocks
│   ├── test_config_readers.py     → lectores de archivos de configuración
│   └── test_writers.py            → escritores de resultados
└── integration/
    ├── __init__.py
    └── test_full_processing.py    → flujo completo con archivos reales
```

---

## 3. Fixtures compartidos (`conftest.py`)

```python
# tests/conftest.py

import pytest
from datetime import date
from cab.domain.models import CaseInput, ContractItem, AccountClosure
from cab.application.ports import BalanceNotFoundError


@pytest.fixture
def case_input_positive():
    """Caso con saldo positivo."""
    return CaseInput(
        caseId="CASE_001",
        source="CLI",
        contracts=[ContractItem(contractId="ACC_001")],
        accountClosure=AccountClosure(),
    )


@pytest.fixture
def case_input_zero():
    """Caso con saldo cero."""
    return CaseInput(
        caseId="CASE_002",
        source="CLI",
        contracts=[ContractItem(contractId="ACC_002")],
        accountClosure=AccountClosure(),
    )


@pytest.fixture
def case_input_negative():
    """Caso con saldo negativo sin fecha."""
    return CaseInput(
        caseId="CASE_003",
        source="CLI",
        contracts=[ContractItem(contractId="ACC_003")],
        accountClosure=AccountClosure(),
    )


@pytest.fixture
def case_input_negative_cancel():
    """Caso con saldo negativo y fecha = hoy."""
    return CaseInput(
        caseId="CASE_004",
        source="CLI",
        contracts=[ContractItem(contractId="ACC_003")],
        accountClosure=AccountClosure(dateToCheckBalance=date.today()),
    )


# --- Mocks de puertos ---

class MockBalanceProvider:
    def __init__(self, balances: dict[str, float]):
        self._balances = balances

    def get_balance(self, account_id: str) -> float:
        if account_id not in self._balances:
            raise BalanceNotFoundError(account_id)
        return self._balances[account_id]


class MockCalendarProvider:
    def __init__(self, non_working: list[date] | None = None):
        self._days = non_working or []

    def get_non_working_days(self) -> list[date]:
        return self._days


class MockRulesProvider:
    def __init__(self, days: int = 3):
        self._days = days

    def get_days_to_check_balance(self) -> int:
        return self._days
```

---

## 4. Tests de dominio — Reglas de decisión

Son los tests más importantes: verifican la lógica pura sin ninguna dependencia externa.

```python
# tests/unit/test_domain_rules.py

from datetime import date, datetime
from cab.domain.models import CaseInput, ContractItem, AccountClosure, Action
from cab.domain.rules import decide_action, calculate_working_day


class TestDecideAction:

    def test_positive_balance_returns_positive_action(self, case_input_positive):
        result = decide_action(
            case_input=case_input_positive,
            balance=120.50,
            today=date(2026, 3, 23),
            non_working_days=[],
            days_to_check=3,
        )
        assert result.action == Action.POSITIVE_BALANCE
        assert result.date_time is None

    def test_zero_balance_returns_zero_action(self, case_input_zero):
        result = decide_action(
            case_input=case_input_zero,
            balance=0,
            today=date(2026, 3, 23),
            non_working_days=[],
            days_to_check=3,
        )
        assert result.action == Action.ZERO_BALANCE
        assert result.date_time is None

    def test_negative_balance_without_date_returns_wait(self, case_input_negative):
        result = decide_action(
            case_input=case_input_negative,
            balance=-45.20,
            today=date(2026, 3, 23),  # lunes
            non_working_days=[],
            days_to_check=3,
        )
        assert result.action == Action.WAIT
        assert result.date_time is not None

    def test_negative_balance_date_equals_today_returns_cancel(self):
        case = CaseInput(
            caseId="CASE_X",
            source="CLI",
            contracts=[ContractItem(contractId="ACC_003")],
            accountClosure=AccountClosure(dateToCheckBalance=date(2026, 3, 23)),
        )
        result = decide_action(
            case_input=case,
            balance=-10,
            today=date(2026, 3, 23),
            non_working_days=[],
            days_to_check=3,
        )
        assert result.action == Action.CANCEL

    def test_negative_balance_date_not_today_returns_wait(self):
        future = date(2026, 3, 25)
        case = CaseInput(
            caseId="CASE_Y",
            source="CLI",
            contracts=[ContractItem(contractId="ACC_003")],
            accountClosure=AccountClosure(dateToCheckBalance=future),
        )
        result = decide_action(
            case_input=case,
            balance=-10,
            today=date(2026, 3, 23),
            non_working_days=[],
            days_to_check=3,
        )
        assert result.action == Action.WAIT
        assert result.date_time == datetime(2026, 3, 25, 0, 1)


class TestCalculateWorkingDay:

    def test_skips_weekend(self):
        # Viernes 2026-03-27 + 1 día hábil = Lunes 2026-03-30
        result = calculate_working_day(date(2026, 3, 27), 1, [])
        assert result == date(2026, 3, 30)

    def test_skips_holidays(self):
        holidays = [date(2026, 3, 24)]
        # Lunes 2026-03-23 + 1 día hábil, saltando el 24 = 25
        result = calculate_working_day(date(2026, 3, 23), 1, holidays)
        assert result == date(2026, 3, 25)

    def test_three_working_days_no_holidays(self):
        # Lunes 23 + 3 días hábiles = Jueves 26
        result = calculate_working_day(date(2026, 3, 23), 3, [])
        assert result == date(2026, 3, 26)

    def test_three_working_days_with_weekend(self):
        # Jueves 26 + 3 días hábiles = Miércoles 1 abril
        # (salta sáb 28, dom 29)
        result = calculate_working_day(date(2026, 3, 26), 3, [])
        assert result == date(2026, 3, 31)
```

---

## 5. Tests de aplicación — Procesador

Verifican que el procesador orquesta correctamente los puertos y las reglas.

```python
# tests/unit/test_processor.py

import pytest
from cab.application.processor import CheckAccountBalanceProcessor
from cab.application.ports import ProcessingError
from cab.domain.models import Action, CaseInput, ContractItem


class TestProcessor:

    def setup_method(self):
        from tests.conftest import MockBalanceProvider, MockCalendarProvider, MockRulesProvider
        self.processor = CheckAccountBalanceProcessor(
            balance_provider=MockBalanceProvider({"ACC_001": 120.50, "ACC_002": 0, "ACC_003": -45.20}),
            calendar_provider=MockCalendarProvider(),
            rules_provider=MockRulesProvider(),
        )

    def test_processes_positive_balance(self, case_input_positive):
        result = self.processor.process(case_input_positive)
        assert result.action == Action.POSITIVE_BALANCE

    def test_raises_error_for_unknown_account(self):
        case = CaseInput(
            caseId="CASE_X",
            source="CLI",
            contracts=[ContractItem(contractId="ACC_999")],
        )
        with pytest.raises(ProcessingError) as exc_info:
            self.processor.process(case)
        assert exc_info.value.code == "ERR001"

    def test_raises_error_for_empty_contracts(self):
        case = CaseInput(caseId="CASE_Y", source="CLI", contracts=[])
        with pytest.raises(ProcessingError) as exc_info:
            self.processor.process(case)
        assert exc_info.value.code == "ERR002"
```

---

## 6. Tests de infraestructura — Adaptadores

Verifican que los lectores y escritores de archivos funcionan correctamente.

```python
# tests/unit/test_config_readers.py

import json
import pytest
from pathlib import Path
from cab.infrastructure.filesystem.config_readers import (
    FileBalanceProvider,
    FileCalendarProvider,
    FileRulesProvider,
)
from cab.application.ports import BalanceNotFoundError


class TestFileBalanceProvider:

    def test_returns_balance_for_known_account(self, tmp_path):
        (tmp_path / "balances.json").write_text('{"ACC_001": 120.50}')
        provider = FileBalanceProvider(tmp_path)
        assert provider.get_balance("ACC_001") == 120.50

    def test_raises_for_unknown_account(self, tmp_path):
        (tmp_path / "balances.json").write_text('{"ACC_001": 120.50}')
        provider = FileBalanceProvider(tmp_path)
        with pytest.raises(BalanceNotFoundError):
            provider.get_balance("ACC_999")


class TestFileCalendarProvider:

    def test_returns_non_working_days(self, tmp_path):
        data = {"non_working_days": ["2026-03-28"]}
        (tmp_path / "calendar.json").write_text(json.dumps(data))
        provider = FileCalendarProvider(tmp_path)
        days = provider.get_non_working_days()
        assert len(days) == 1


class TestFileRulesProvider:

    def test_returns_days_to_check(self, tmp_path):
        (tmp_path / "rules.json").write_text('{"daysToCheckBalance": 3}')
        provider = FileRulesProvider(tmp_path)
        assert provider.get_days_to_check_balance() == 3
```

```python
# tests/unit/test_writers.py

import json
from datetime import datetime
from cab.domain.models import DomainResult, Action
from cab.infrastructure.filesystem.writers import OutputWriter, ErrorWriter


class TestOutputWriter:

    def test_writes_success_result(self, tmp_path):
        writer = OutputWriter(tmp_path)
        result = DomainResult(case_id="CASE_001", action=Action.POSITIVE_BALANCE)
        writer.write(result)

        output_file = tmp_path / "CASE_001.json"
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["caseId"] == "CASE_001"
        assert data["action"] == "positiveBalance"
        assert data["dateTime"] is None


class TestErrorWriter:

    def test_writes_error_result(self, tmp_path):
        writer = ErrorWriter(tmp_path)
        writer.write("CASE_001", [{"code": "ERR001", "message": "Test error"}])

        error_file = tmp_path / "CASE_001_error.json"
        assert error_file.exists()
        data = json.loads(error_file.read_text())
        assert data["caseId"] == "CASE_001"
        assert len(data["errors"]) == 1
```

---

## 7. Test de integración — Flujo completo

Verifica el sistema de extremo a extremo con archivos reales.

```python
# tests/integration/test_full_processing.py

import json
from pathlib import Path
from cab.application.processor import CheckAccountBalanceProcessor
from cab.application.service import FileProcessingService
from cab.infrastructure.filesystem.config_readers import (
    FileBalanceProvider, FileCalendarProvider, FileRulesProvider,
)
from cab.infrastructure.filesystem.writers import OutputWriter, ErrorWriter


def _setup_data(tmp_path: Path) -> dict[str, Path]:
    """Crea la estructura de datos completa para tests."""
    dirs = {}
    for name in ["inbox", "processing", "outbox", "errors", "config"]:
        d = tmp_path / name
        d.mkdir()
        dirs[name] = d

    # Configuración
    (dirs["config"] / "balances.json").write_text(
        json.dumps({"ACC_001": 120.50, "ACC_002": 0, "ACC_003": -45.20})
    )
    (dirs["config"] / "calendar.json").write_text(
        json.dumps({"non_working_days": []})
    )
    (dirs["config"] / "rules.json").write_text(
        json.dumps({"daysToCheckBalance": 3})
    )

    return dirs


class TestFullProcessing:

    def test_positive_balance_case(self, tmp_path):
        dirs = _setup_data(tmp_path)

        # Crear caso en inbox
        case = {
            "caseId": "CASE_001",
            "source": "CLI",
            "contracts": [{"contractId": "ACC_001"}],
            "accountClosure": {}
        }
        (dirs["inbox"] / "CASE_001.json").write_text(json.dumps(case))

        # Construir y ejecutar
        processor = CheckAccountBalanceProcessor(
            balance_provider=FileBalanceProvider(dirs["config"]),
            calendar_provider=FileCalendarProvider(dirs["config"]),
            rules_provider=FileRulesProvider(dirs["config"]),
        )
        service = FileProcessingService(
            inbox_dir=dirs["inbox"],
            processing_dir=dirs["processing"],
            processor=processor,
            output_writer=OutputWriter(dirs["outbox"]),
            error_writer=ErrorWriter(dirs["errors"]),
        )

        count = service.process_all()
        assert count == 1

        # Verificar resultado
        result_file = dirs["outbox"] / "CASE_001.json"
        assert result_file.exists()
        data = json.loads(result_file.read_text())
        assert data["action"] == "positiveBalance"

    def test_unknown_account_produces_error(self, tmp_path):
        dirs = _setup_data(tmp_path)

        case = {
            "caseId": "CASE_ERR",
            "source": "CLI",
            "contracts": [{"contractId": "ACC_999"}],
        }
        (dirs["inbox"] / "CASE_ERR.json").write_text(json.dumps(case))

        processor = CheckAccountBalanceProcessor(
            balance_provider=FileBalanceProvider(dirs["config"]),
            calendar_provider=FileCalendarProvider(dirs["config"]),
            rules_provider=FileRulesProvider(dirs["config"]),
        )
        service = FileProcessingService(
            inbox_dir=dirs["inbox"],
            processing_dir=dirs["processing"],
            processor=processor,
            output_writer=OutputWriter(dirs["outbox"]),
            error_writer=ErrorWriter(dirs["errors"]),
        )

        service.process_all()

        error_file = dirs["errors"] / "CASE_ERR_error.json"
        assert error_file.exists()
```

---

## 8. Cobertura mínima de casos de prueba

Según la especificación, deben cubrirse al menos:

| Caso | Test | Acción esperada |
|---|---|---|
| Saldo positivo | `test_positive_balance_*` | `positiveBalance` |
| Saldo cero | `test_zero_balance_*` | `zeroBalance` |
| Saldo negativo, origen cliente | `test_negative_balance_*` (source=CLI) | `wait` |
| Saldo negativo, origen banco | `test_negative_balance_*` (source=BATCH) | `wait` |
| Caso con espera (wait) | `test_negative_balance_without_date_*` | `wait` + fecha |
| Caso con cancelación | `test_negative_balance_date_equals_today_*` | `cancel` |
| Cuenta inexistente | `test_unknown_account_*` | error ERR001 |
| Caso sin contratos | `test_empty_contracts_*` | error ERR002 |

---

## 9. Ejecutar tests

```bash
# Todos los tests
pytest tests/ -v

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v

# Con cobertura
pytest tests/ --cov=cab --cov-report=term-missing
```

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] Existen tests unitarios para reglas de dominio (al menos 6 escenarios)
- [ ] Existen tests unitarios para el procesador (éxito y errores)
- [ ] Existen tests unitarios para los adaptadores de archivos
- [ ] Existe al menos un test de integración de flujo completo
- [ ] Todos los tests pasan con `pytest tests/ -v`
- [ ] Los mocks de puertos no requieren herencia ni frameworks
