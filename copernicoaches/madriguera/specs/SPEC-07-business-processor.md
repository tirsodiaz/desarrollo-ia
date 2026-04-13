# SPEC-07 — Business Processor: Check Account Balance

## Goal

Implement the `CheckAccountBalanceProcessor`, `ProcessStage`, and `PersistStage`. Together these take a validated `CaseInput` from the envelope, apply the decision rules defined in SPEC-02, record the result in the database, and populate the envelope with a `DomainResult` ready for output writing.

---

## Scope

- `CheckAccountBalanceProcessor`: the domain processor that calls external adapters and applies rules
- `ProcessStage`: the pipeline stage that invokes the processor
- `PersistStage`: the pipeline stage that writes the result back to the database
- Integration of all previously built components: domain rules, config adapters, persistence

---

## Deliverables

### 1. Processor interface — `src/app/application/ports.py`

Add to the existing `ports.py`:

```python
class BusinessProcessor(Protocol):
    def process(self, case_input: CaseInput) -> DomainResult:
        """
        Apply business rules and return a DomainResult.
        Raises ProcessingError on unrecoverable failure.
        """
        ...
```

Define:

```python
class ProcessingError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message
```

### 2. Processor implementation — `src/app/application/check_balance_processor.py`

```python
from datetime import date
from app.domain.models import CaseInput, DomainResult
from app.domain.rules import decide_action, calculate_working_day
from app.application.ports import BalanceProvider, CalendarProvider, RulesProvider, ProcessingError

class CheckAccountBalanceProcessor:
    def __init__(
        self,
        balance_provider: BalanceProvider,
        calendar_provider: CalendarProvider,
        rules_provider: RulesProvider,
    ):
        self._balances = balance_provider
        self._calendar = calendar_provider
        self._rules = rules_provider

    def process(self, case_input: CaseInput) -> DomainResult:
        account_id = case_input.contracts[0].contractId

        try:
            balance = self._balances.get_balance(account_id)
        except BalanceNotFoundError as e:
            raise ProcessingError(
                code="ERR_BALANCE_NOT_FOUND",
                message=f"No balance configured for account: {account_id}",
            ) from e

        non_working_days = self._calendar.get_non_working_days()
        days_to_check = self._rules.get_days_to_check_balance()
        today = date.today()

        return decide_action(
            case_input=case_input,
            balance=balance,
            today=today,
            working_day_calculator=calculate_working_day,
            non_working_days=non_working_days,
            days_to_check=days_to_check,
        )
```

The processor has no knowledge of files, the pipeline, or the database.

### 3. ProcessStage — `src/app/pipeline/stages.py`

Replace the stub:

```python
class ProcessStage(BaseStage):
    name = "process"

    def __init__(self, processor: BusinessProcessor):
        self._processor = processor

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        case_input: CaseInput = envelope.domain_input  # type: ignore
        if case_input is None:
            return self._fail(envelope, "ERR_PROCESS_NO_INPUT", "domain_input is None")
        try:
            envelope.domain_result = self._processor.process(case_input)
            return envelope
        except ProcessingError as e:
            return self._fail(envelope, e.code, e.message)
        except Exception as e:
            return self._fail(envelope, "ERR_PROCESS_UNEXPECTED", str(e))
```

### 4. PersistStage — `src/app/pipeline/stages.py`

Replace the stub:

```python
class PersistStage(BaseStage):
    name = "persist"

    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        self._uow_factory = uow_factory

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        result: DomainResult = envelope.domain_result  # type: ignore
        if result is None:
            return self._fail(envelope, "ERR_PERSIST_NO_RESULT", "domain_result is None")
        try:
            with self._uow_factory() as uow:
                uow.records.update_status(
                    correlation_id=envelope.correlation_id,
                    status="PROCESSING",
                    action=result.action,
                    started_at=envelope.started_at,
                )
            return envelope
        except Exception as e:
            return self._fail(envelope, "ERR_PERSIST_DB_ERROR", str(e))
```

Note: final status update (`SUCCESS` / `ERROR`) is handled by `FileProcessingService.handle` after the full pipeline completes (SPEC-06). `PersistStage` only records the intermediate state and the action.

### 5. Update `build_pipeline` factory — `src/app/pipeline/engine.py`

Update the factory to inject real dependencies:

```python
def build_pipeline(settings: AppSettings) -> PipelineEngine:
    balance_provider = FileBalanceProvider(settings.config_dir)
    calendar_provider = FileCalendarProvider(settings.config_dir)
    rules_provider = FileRulesProvider(settings.config_dir)

    processor = CheckAccountBalanceProcessor(
        balance_provider=balance_provider,
        calendar_provider=calendar_provider,
        rules_provider=rules_provider,
    )

    uow_factory = lambda: UnitOfWork(build_session_factory(settings.database_url))

    stages = [
        IngestStage(processing_dir=settings.processing_dir),
        ParseStage(),
        ValidateStage(),
        ProcessStage(processor=processor),
        PersistStage(uow_factory=uow_factory),
        EmitStage(outbox_dir=settings.outbox_dir, errors_dir=settings.errors_dir),
        ArchiveStage(archive_dir=settings.archive_dir),
    ]
    return PipelineEngine(stages)
```

---

## Validations

### V-01 — Processor returns positiveBalance for positive account

```python
def test_processor_positive_balance():
    balance_provider = MockBalanceProvider({"ACC_001": 120.50})
    calendar_provider = MockCalendarProvider([])
    rules_provider = MockRulesProvider(3)

    processor = CheckAccountBalanceProcessor(balance_provider, calendar_provider, rules_provider)
    case = CaseInput(
        caseId="CASE_001", source="CLI",
        contracts=[ContractItem(contractId="ACC_001")],
        accountClosure=AccountClosure(entity="0014"),
    )
    result = processor.process(case)
    assert result.action == Action.POSITIVE_BALANCE
```

### V-02 — Processor raises ProcessingError for unknown account

```python
def test_processor_unknown_account():
    balance_provider = MockBalanceProvider({})
    processor = CheckAccountBalanceProcessor(balance_provider, MockCalendarProvider([]), MockRulesProvider(3))
    case = CaseInput(caseId="X", source="CLI",
                     contracts=[ContractItem(contractId="UNKNOWN")],
                     accountClosure=AccountClosure(entity="0014"))
    with pytest.raises(ProcessingError) as exc_info:
        processor.process(case)
    assert exc_info.value.code == "ERR_BALANCE_NOT_FOUND"
```

### V-03 — ProcessStage sets domain_result on success

```python
def test_process_stage_success(envelope_with_case_input, mock_processor):
    stage = ProcessStage(processor=mock_processor)
    result = stage.execute(envelope_with_case_input)
    assert result.status != PipelineStatus.ERROR
    assert isinstance(result.domain_result, DomainResult)
```

### V-04 — ProcessStage fails gracefully on ProcessingError

```python
def test_process_stage_processing_error(envelope_with_case_input):
    class ErrorProcessor:
        def process(self, _):
            raise ProcessingError("ERR_TEST", "test error")

    result = ProcessStage(ErrorProcessor()).execute(envelope_with_case_input)
    assert result.status == PipelineStatus.ERROR
    assert result.error_code == "ERR_TEST"
```

### V-05 — PersistStage writes action to database

```python
def test_persist_stage_writes_action(tmp_path, uow_factory, envelope_with_domain_result):
    stage = PersistStage(uow_factory=uow_factory)
    result = stage.execute(envelope_with_domain_result)
    assert result.status != PipelineStatus.ERROR

    with uow_factory() as uow:
        record = uow.records.get_by_correlation_id(envelope_with_domain_result.correlation_id)
        assert record.action == "positiveBalance"
```

### V-06 — Full pipeline with real config files (integration test)

```python
def test_full_pipeline_positive_case(tmp_path):
    # Set up directories and config files
    setup_test_dirs(tmp_path)
    write_config(tmp_path, balances={"ACC_001": 120.50}, rules={"daysToCheckBalance": 3})
    write_inbox_file(tmp_path, case_id="CASE_001", contract_id="ACC_001", source="CLI")

    # Run pipeline
    settings = AppSettings(
        inbox_dir=tmp_path/"inbox", processing_dir=tmp_path/"processing",
        outbox_dir=tmp_path/"outbox", errors_dir=tmp_path/"errors",
        archive_dir=tmp_path/"archive", config_dir=tmp_path/"config",
        database_url=f"sqlite:///{tmp_path}/test.db"
    )
    pipeline = build_pipeline(settings)
    inbox_file = tmp_path / "inbox" / "case_001.json"
    env = PipelineEnvelope(source_file=inbox_file)
    result = pipeline.run(env)

    assert result.status == PipelineStatus.SUCCESS
    assert result.domain_result.action == Action.POSITIVE_BALANCE
```

### V-07 — Mock adapter fixtures

Define mock adapters in `tests/unit/conftest.py` for reuse across tests:

```python
class MockBalanceProvider:
    def __init__(self, data: dict): self._data = data
    def get_balance(self, account_id):
        if account_id not in self._data:
            raise BalanceNotFoundError(account_id)
        return self._data[account_id]

class MockCalendarProvider:
    def __init__(self, days): self._days = days
    def get_non_working_days(self): return self._days

class MockRulesProvider:
    def __init__(self, days): self._days = days
    def get_days_to_check_balance(self): return self._days
```

---

## Decisions made

- `today = date.today()` is called inside the processor at runtime. For testing, inject `today` as a parameter to `decide_action` (which already accepts it). The processor calls `date.today()` and passes it in — a `today_provider: Callable[[], date] = date.today` can be injected for testing if needed.
- `PersistStage` only writes intermediate state. Final status is updated by `FileProcessingService`. This split keeps stages focused on their single responsibility and avoids the stage needing to know whether it is the last stage in the pipeline.
- `CheckAccountBalanceProcessor` uses `contracts[0]` (first element). This matches the decision documented in SPEC-02.
- Mock adapters are defined in `conftest.py` and reused across all processor/stage tests. They should **not** use `unittest.mock.MagicMock`; explicit classes are easier to read and maintain.

---

## References

- Domain rules: `madriguera/specs/SPEC-02-domain-models-and-rules.md`
- Config adapters: `madriguera/specs/SPEC-03-config-adapters.md`
- Persistence layer: `madriguera/specs/SPEC-04-persistence-layer.md`
- Pipeline engine: `madriguera/specs/SPEC-05-pipeline-engine.md`
- Architecture guide: `madriguera/architecture-definition.md` — sections "Business processing layer", "Decoupling business operations"
- Functional specification: `dia5/Especificación funcional - Simulación de proceso automático de verificación de saldo.md` — sections 6, 7, 8
