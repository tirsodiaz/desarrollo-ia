# SPEC-03 — Simulated External Adapters (Config-File Readers)

## Goal

Implement the infrastructure components that simulate the three external dependencies required by the business logic: account balances, the working-day calendar, and processing rules. All three are read from JSON files inside the `config/` directory. No real API calls are made.

---

## Scope

- Balance reader: loads `config/balances.json` and returns a balance for a given `account_id`
- Calendar reader: loads `config/calendar.json` and returns a list of non-working dates
- Rules reader: loads `config/rules.json` and returns the `daysToCheckBalance` parameter
- A seed script / fixture that creates sample config files for manual testing
- Unit tests for all three readers

---

## Config file formats

### `data/config/balances.json`

A flat JSON object mapping `accountId` strings to float balances:

```json
{
  "ACC_001": 120.50,
  "ACC_002": 0.0,
  "ACC_003": -45.20,
  "ACC_004": -10.00
}
```

### `data/config/calendar.json`

A JSON object with a `non_working_days` array of ISO date strings:

```json
{
  "non_working_days": [
    "2026-03-23",
    "2026-04-02",
    "2026-04-03"
  ]
}
```

Weekends (Saturday, Sunday) are always non-working regardless of this list. The calendar file records only holidays and bank holidays.

### `data/config/rules.json`

A JSON object with processing parameters:

```json
{
  "daysToCheckBalance": 3
}
```

---

## Deliverables

### 1. Interfaces — `src/app/application/ports.py`

Define abstract base classes (protocols) for each external capability. The business processor will depend on these interfaces, not on the file-based implementations.

```python
from typing import Protocol
from datetime import date

class BalanceProvider(Protocol):
    def get_balance(self, account_id: str) -> float:
        """Raises BalanceNotFoundError if account_id is unknown."""

class CalendarProvider(Protocol):
    def get_non_working_days(self) -> list[date]:
        """Returns all configured non-working days (holidays only, not weekends)."""

class RulesProvider(Protocol):
    def get_days_to_check_balance(self) -> int:
        """Returns the number of working days used to calculate the check date."""
```

Define a custom exception in the same file:

```python
class BalanceNotFoundError(Exception):
    def __init__(self, account_id: str):
        super().__init__(f"Balance not found for account: {account_id}")
        self.account_id = account_id
```

### 2. File-based implementations — `src/app/infrastructure/filesystem/config_readers.py`

Implement the three protocols using plain JSON file reads.

#### `FileBalanceProvider`

```python
class FileBalanceProvider:
    def __init__(self, config_dir: Path):
        self._path = config_dir / "balances.json"

    def get_balance(self, account_id: str) -> float:
        data = json.loads(self._path.read_text())
        if account_id not in data:
            raise BalanceNotFoundError(account_id)
        return float(data[account_id])
```

#### `FileCalendarProvider`

```python
class FileCalendarProvider:
    def __init__(self, config_dir: Path):
        self._path = config_dir / "calendar.json"

    def get_non_working_days(self) -> list[date]:
        data = json.loads(self._path.read_text())
        return [date.fromisoformat(d) for d in data.get("non_working_days", [])]
```

#### `FileRulesProvider`

```python
class FileRulesProvider:
    def __init__(self, config_dir: Path):
        self._path = config_dir / "rules.json"

    def get_days_to_check_balance(self) -> int:
        data = json.loads(self._path.read_text())
        return int(data["daysToCheckBalance"])
```

All three classes must raise `FileNotFoundError` (Python built-in) if the config file does not exist. Do not swallow that error.

### 3. Sample config fixture — `data/config/` (committed to repo)

Create the following files with realistic sample data that covers all test scenarios:

**`data/config/balances.json`**
```json
{
  "ACC_001": 120.50,
  "ACC_002": 0.0,
  "ACC_003": -45.20,
  "ACC_004": -10.00,
  "ACC_005": -75.00
}
```

**`data/config/calendar.json`**
```json
{
  "non_working_days": []
}
```

**`data/config/rules.json`**
```json
{
  "daysToCheckBalance": 3
}
```

### 4. Sample inbox files — `data/inbox/` (committed to repo)

Create one sample JSON file per scenario to cover all required test cases:

| File | caseId | contracts[0] | source | dateToCheckBalance | Expected action |
|---|---|---|---|---|---|
| `case_positive.json` | CASE_001 | ACC_001 | CLI | null | positiveBalance |
| `case_zero.json` | CASE_002 | ACC_002 | CLI | null | zeroBalance |
| `case_neg_cli.json` | CASE_003 | ACC_003 | CLI | null | wait |
| `case_neg_bank.json` | CASE_004 | ACC_004 | BANK | null | wait |
| `case_wait.json` | CASE_005 | ACC_005 | BANK | 2026-03-25 | wait |
| `case_cancel.json` | CASE_006 | ACC_005 | BANK | 2026-03-20 | cancel |

Each file follows the format defined in SPEC-02 `CaseInput`.

---

## Validations

### V-01 — Balance found

```python
provider = FileBalanceProvider(Path("data/config"))
assert provider.get_balance("ACC_001") == 120.50
```

### V-02 — Balance not found raises BalanceNotFoundError

```python
with pytest.raises(BalanceNotFoundError) as exc_info:
    provider.get_balance("UNKNOWN")
assert exc_info.value.account_id == "UNKNOWN"
```

### V-03 — Calendar returns parsed dates

```python
# Given calendar.json contains "2026-03-23"
provider = FileCalendarProvider(Path("tests/fixtures/config"))
days = provider.get_non_working_days()
assert date(2026, 3, 23) in days
```

### V-04 — Rules returns integer

```python
provider = FileRulesProvider(Path("data/config"))
assert provider.get_days_to_check_balance() == 3
```

### V-05 — Missing config file raises FileNotFoundError

```python
provider = FileBalanceProvider(Path("/nonexistent"))
with pytest.raises(FileNotFoundError):
    provider.get_balance("ACC_001")
```

### V-06 — Providers satisfy their Protocol interfaces

```python
from app.application.ports import BalanceProvider, CalendarProvider, RulesProvider
from app.infrastructure.filesystem.config_readers import (
    FileBalanceProvider, FileCalendarProvider, FileRulesProvider
)

# Static type check: these should pass mypy / pyright
bp: BalanceProvider = FileBalanceProvider(Path("data/config"))
cp: CalendarProvider = FileCalendarProvider(Path("data/config"))
rp: RulesProvider = FileRulesProvider(Path("data/config"))
```

### V-07 — All six sample inbox files are valid CaseInput

```python
import json
from app.domain.models import CaseInput

for path in Path("data/inbox").glob("*.json"):
    payload = json.loads(path.read_text())
    case = CaseInput.model_validate(payload)
    assert case.caseId is not None
```

---

## Decisions made

- Config files are read fresh on every call (no in-memory caching). This keeps the implementation simple and testable. A caching layer can be added later without changing the interface.
- The `calendar.json` file records only explicit holidays. Weekends are always excluded by the working-day calculator in `rules.py` (SPEC-02). This avoids duplicating weekend data in the config.
- `FileRulesProvider` raises `KeyError` if `daysToCheckBalance` is absent. This is an intentional fail-fast: a misconfigured system should crash loudly, not silently use a wrong default.
- The `entity` field in `AccountClosure` is present in the original process diagram for calendar selection (`0014 → calendarId 3`, `ZE00 → calendarId 1`). In this simulation the entity is not used for calendar selection because there is a single flat calendar file. The entity field is preserved in the model for future use.

---

## References

- Functional specification: `dia5/Especificación funcional - Simulación de proceso automático de verificación de saldo.md` — sections 3, 4, 5
- Process analysis: `dia2/first_analysis/Process.md` — "Calendar-dependent calculation", "Resolve the account and retrieve balances"
- Services analysis: `dia2/first_analysis/Services.md` — "Get account balances", "Get calendar dates"
- Architecture guide: `madriguera/architecture-definition.md` — "Business logic must be isolated", "Replaceability"
