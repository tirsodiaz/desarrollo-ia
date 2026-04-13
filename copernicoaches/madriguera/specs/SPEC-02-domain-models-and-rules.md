# SPEC-02 — Domain Models & Decision Rules

## Goal

Define all Pydantic schemas used as typed contracts at pipeline boundaries and implement the core decision logic as pure functions with no I/O dependencies. This spec produces the business heart of the application; it must be fully testable without touching the file system or any database.

---

## Scope

- Pydantic v2 models for inbound case payload, domain input, domain result, output artifact, and error artifact
- Decision rules as a pure function
- Working-day date calculation as a pure function
- Unit tests covering all decision branches

---

## Deliverables

### 1. Input model — `src/app/domain/models.py`

Define the following Pydantic models representing the inbound case JSON file.

#### `ContractItem`
```python
class ContractItem(BaseModel):
    contractId: str
```

#### `AccountClosure`
```python
class AccountClosure(BaseModel):
    dateToCheckBalance: date | None = None
    entity: str
```

#### `CaseInput`
```python
class CaseInput(BaseModel):
    caseId: str
    source: str
    contracts: list[ContractItem]
    accountClosure: AccountClosure
```

All fields are required except `dateToCheckBalance` which is nullable.

`source` values are treated as plain strings; case-sensitive comparison to `"CLI"` determines the negative-balance branch.

`contracts` must have at least one element. The **first element** (`contracts[0]`) is used as the account to query. This resolves the ambiguity noted in the original process diagram (`contracts[1]` — 1-indexed). Document this decision as a comment.

#### `BalanceData`
```python
class BalanceData(BaseModel):
    account_id: str
    amount: float
```

### 2. Result action enum — `src/app/domain/models.py`

```python
from enum import StrEnum

class Action(StrEnum):
    POSITIVE_BALANCE = "positiveBalance"
    ZERO_BALANCE = "zeroBalance"
    CUSTOMER_NEGATIVE_BALANCE = "customerNegativeBalance"
    BANK_NEGATIVE_BALANCE = "bankNegativeBalance"
    WAIT = "wait"
    CANCEL = "cancel"
```

### 3. Domain result — `src/app/domain/models.py`

```python
class DomainResult(BaseModel):
    case_id: str
    action: Action
    date_time: datetime | None = None
```

`date_time` is populated only when `action == Action.WAIT`. Its value must be `<next_working_day> at 00:01:00`.

### 4. Output artifact — `src/app/domain/models.py`

```python
class OutputPayload(BaseModel):
    caseId: str
    action: str
    dateTime: str | None = None
```

`dateTime` is serialised as ISO 8601 string when present, `null` otherwise.

### 5. Error artifact — `src/app/domain/models.py`

```python
class ErrorEntry(BaseModel):
    code: str
    message: str

class ErrorPayload(BaseModel):
    caseId: str
    taskName: str = "Check Account Balance"
    dateTime: str          # ISO 8601 timestamp of the failure
    errors: list[ErrorEntry]
```

---

### 6. Decision rules — `src/app/domain/rules.py`

Implement one pure function:

```python
def decide_action(
    case_input: CaseInput,
    balance: float,
    today: date,
    working_day_calculator: Callable[[date, int, list[date]], date],
    non_working_days: list[date],
    days_to_check: int,
) -> DomainResult:
```

**Logic** (matches the functional specification exactly):

1. If `balance > 0` → return `Action.POSITIVE_BALANCE`, `date_time = None`
2. If `balance == 0` → return `Action.ZERO_BALANCE`, `date_time = None`
3. If `balance < 0`:
   a. Determine sub-action from `source`:
      - `source == "CLI"` → `sub_action = Action.CUSTOMER_NEGATIVE_BALANCE`
      - otherwise → `sub_action = Action.BANK_NEGATIVE_BALANCE`
   b. Evaluate `dateToCheckBalance`:
      - If `None` (not present): calculate future date using `working_day_calculator(today, days_to_check, non_working_days)`. Return `Action.WAIT` with `date_time = calculated_date at 00:01:00`.
      - If equals `today`: return `Action.CANCEL`, `date_time = None`
      - Otherwise (date exists but is not today): return `Action.WAIT`, `date_time = dateToCheckBalance at 00:01:00`

Note: `sub_action` (`customerNegativeBalance` / `bankNegativeBalance`) is **not** the final returned action when `dateToCheckBalance` is involved. When the date path is taken (`wait` or `cancel`), the `sub_action` is implicit context but the returned action is `wait` or `cancel`. This matches the functional specification section 7 and the process diagram.

---

### 7. Working-day calculator — `src/app/domain/rules.py`

Implement one pure function:

```python
def calculate_working_day(
    from_date: date,
    days_ahead: int,
    non_working_days: list[date],
) -> date:
```

**Logic:**
1. Start from `from_date + 1 day` (i.e. tomorrow)
2. Advance `days_ahead` working days, skipping any date that appears in `non_working_days` or is a Saturday/Sunday
3. Return the resulting date

**Example:** if `today = 2026-03-20` (Friday), `days_ahead = 3`, and no holidays: skip Saturday 21, Sunday 22, count Monday 23 (day 1), Tuesday 24 (day 2), Wednesday 25 (day 3) → return `2026-03-25`.

---

## Validations

### V-01 — Positive balance

```python
result = decide_action(case_input, balance=120.50, today=date(2026,3,20), ...)
assert result.action == Action.POSITIVE_BALANCE
assert result.date_time is None
```

### V-02 — Zero balance

```python
result = decide_action(case_input, balance=0.0, today=date(2026,3,20), ...)
assert result.action == Action.ZERO_BALANCE
```

### V-03 — Negative balance, CLI source, no existing date → WAIT with calculated date

```python
case_input = CaseInput(caseId="X", source="CLI",
    contracts=[ContractItem(contractId="ACC")],
    accountClosure=AccountClosure(dateToCheckBalance=None, entity="0014"))
result = decide_action(case_input, balance=-45.0, today=date(2026,3,20),
    working_day_calculator=calculate_working_day,
    non_working_days=[], days_to_check=3)
assert result.action == Action.WAIT
assert result.date_time is not None
assert result.date_time.date() == date(2026, 3, 25)  # 3 working days from Friday
assert result.date_time.time() == time(0, 1, 0)
```

### V-04 — Negative balance, non-CLI source, existing date = today → CANCEL

```python
case_input = CaseInput(..., source="BANK",
    accountClosure=AccountClosure(dateToCheckBalance=date(2026,3,20), entity="0014"))
result = decide_action(case_input, balance=-10.0, today=date(2026,3,20), ...)
assert result.action == Action.CANCEL
```

### V-05 — Negative balance, existing date ≠ today → WAIT with existing date

```python
case_input = CaseInput(..., source="BANK",
    accountClosure=AccountClosure(dateToCheckBalance=date(2026,3,25), entity="0014"))
result = decide_action(case_input, balance=-10.0, today=date(2026,3,20), ...)
assert result.action == Action.WAIT
assert result.date_time.date() == date(2026, 3, 25)
```

### V-06 — Working-day calculator skips weekends

```python
d = calculate_working_day(date(2026,3,20), days_ahead=1, non_working_days=[])
assert d == date(2026, 3, 23)  # Monday, skipping Sat+Sun
```

### V-07 — Working-day calculator skips holidays

```python
holiday = date(2026, 3, 23)  # Monday is a holiday
d = calculate_working_day(date(2026,3,20), days_ahead=1, non_working_days=[holiday])
assert d == date(2026, 3, 24)  # Tuesday
```

### V-08 — CaseInput rejects missing caseId

```python
with pytest.raises(ValidationError):
    CaseInput(source="CLI", contracts=[], accountClosure=...)
```

### V-09 — Action enum serialises to expected strings

```python
assert Action.POSITIVE_BALANCE == "positiveBalance"
assert Action.CUSTOMER_NEGATIVE_BALANCE == "customerNegativeBalance"
```

---

## Decisions made

- `contracts[0]` (first element, 0-indexed) is used as the primary account. The original diagram uses 1-based notation (`contracts[1]`), which has been normalised to 0-indexed Python convention.
- The negative-balance sub-action (`customerNegativeBalance` / `bankNegativeBalance`) is not exposed as a direct `action` in the `WAIT`/`CANCEL` path. The final action is always `wait` or `cancel` in that path. This matches the functional specification table in section 7.
- `balance == 0.0` is treated as exact float equality. This is sufficient for the simulation; production code would use `Decimal`.
- `StrEnum` is used so `Action.POSITIVE_BALANCE == "positiveBalance"` is `True` without extra serialisation steps.

---

## References

- Functional specification: `dia5/Especificación funcional - Simulación de proceso automático de verificación de saldo.md` — sections 4, 7, 8, 9
- Process analysis: `dia2/first_analysis/Process.md` — sections "Evaluate the balance", "Negative balance logic", "Waiting and cancellation path", "Output contract"
- Architecture guide: `madriguera/architecture-definition.md` — sections "Domain and processing model", "Explicit models at boundaries"
