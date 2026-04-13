import json
from datetime import date
from pathlib import Path

import pytest

from app.application.check_balance_processor import CheckAccountBalanceProcessor
from app.application.ports import ProcessingError
from app.config.settings import AppSettings
from app.domain.models import Action, DomainResult
from app.infrastructure.persistence.session import build_engine, create_all_tables
from app.pipeline.contracts import PipelineEnvelope, PipelineStatus
from app.pipeline.engine import build_pipeline
from app.pipeline.stages import PersistStage, ProcessStage
from tests.unit.conftest import MockBalanceProvider, MockCalendarProvider, MockRulesProvider


def test_processor_positive_balance(case_input) -> None:
    processor = CheckAccountBalanceProcessor(
        balance_provider=MockBalanceProvider({"ACC_001": 120.50}),
        calendar_provider=MockCalendarProvider([]),
        rules_provider=MockRulesProvider(3),
        today_provider=lambda: date(2026, 3, 20),
    )

    result = processor.process(case_input)

    assert result.action == Action.POSITIVE_BALANCE


def test_processor_unknown_account(case_input) -> None:
    case_input.contracts[0].contractId = "UNKNOWN"
    processor = CheckAccountBalanceProcessor(
        balance_provider=MockBalanceProvider({}),
        calendar_provider=MockCalendarProvider([]),
        rules_provider=MockRulesProvider(3),
        today_provider=lambda: date(2026, 3, 20),
    )

    with pytest.raises(ProcessingError) as exc_info:
        processor.process(case_input)

    assert exc_info.value.code == "ERR_BALANCE_NOT_FOUND"


def test_process_stage_success(envelope_with_case_input, case_input) -> None:
    class StaticProcessor:
        def process(self, _: object) -> DomainResult:
            return DomainResult(case_id=case_input.caseId, action=Action.POSITIVE_BALANCE)

    result = ProcessStage(processor=StaticProcessor()).execute(envelope_with_case_input)

    assert result.status != PipelineStatus.ERROR
    assert isinstance(result.domain_result, DomainResult)


def test_process_stage_processing_error(envelope_with_case_input) -> None:
    class ErrorProcessor:
        def process(self, _: object) -> DomainResult:
            raise ProcessingError("ERR_TEST", "test error")

    result = ProcessStage(processor=ErrorProcessor()).execute(envelope_with_case_input)

    assert result.status == PipelineStatus.ERROR
    assert result.error_code == "ERR_TEST"


def test_persist_stage_writes_action(
    uow_factory,
    envelope_with_domain_result,
    persisted_pending_record,
) -> None:
    stage = PersistStage(uow_factory=uow_factory)

    result = stage.execute(envelope_with_domain_result)

    assert result.status != PipelineStatus.ERROR

    with uow_factory() as uow:
        assert uow.records is not None
        record = uow.records.get_by_correlation_id(envelope_with_domain_result.correlation_id)
        assert record is not None
        assert record.action == "positiveBalance"


def test_full_pipeline_positive_case(tmp_path) -> None:
    for name in ("inbox", "processing", "outbox", "errors", "archive", "config"):
        (tmp_path / name).mkdir()

    (tmp_path / "config" / "balances.json").write_text(
        json.dumps({"ACC_001": 120.50}),
        encoding="utf-8",
    )
    (tmp_path / "config" / "calendar.json").write_text(
        json.dumps({"non_working_days": []}),
        encoding="utf-8",
    )
    (tmp_path / "config" / "rules.json").write_text(
        json.dumps({"daysToCheckBalance": 3}),
        encoding="utf-8",
    )

    inbox_file = tmp_path / "inbox" / "case_001.json"
    inbox_file.write_text(
        json.dumps(
            {
                "caseId": "CASE_001",
                "source": "CLI",
                "contracts": [{"contractId": "ACC_001"}],
                "accountClosure": {"dateToCheckBalance": None, "entity": "0014"},
            }
        ),
        encoding="utf-8",
    )

    settings = AppSettings(
        inbox_dir=tmp_path / "inbox",
        processing_dir=tmp_path / "processing",
        outbox_dir=tmp_path / "outbox",
        errors_dir=tmp_path / "errors",
        archive_dir=tmp_path / "archive",
        config_dir=tmp_path / "config",
        database_url=f"sqlite:///{tmp_path}/test.db",
    )
    create_all_tables(build_engine(settings.database_url))
    pipeline = build_pipeline(settings, today_provider=lambda: date(2026, 3, 20))
    envelope = PipelineEnvelope(source_file=Path(inbox_file))

    result = pipeline.run(envelope)

    assert result.status == PipelineStatus.SUCCESS
    assert result.domain_result is not None
    assert result.domain_result.action == Action.POSITIVE_BALANCE
