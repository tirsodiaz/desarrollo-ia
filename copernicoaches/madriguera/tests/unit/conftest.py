from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

from app.application.ports import BalanceNotFoundError, ProcessingRecordCreate
from app.domain.models import (
    AccountClosure,
    Action,
    CaseInput,
    ContractItem,
    DomainResult,
)
from app.infrastructure.persistence.models import Base
from app.infrastructure.persistence.session import build_engine
from app.infrastructure.persistence.uow import UnitOfWork
from app.pipeline.contracts import PipelineEnvelope
from app.time_utils import utc_now


class MockBalanceProvider:
    def __init__(self, data: dict[str, float]):
        self._data = data

    def get_balance(self, account_id: str) -> float:
        if account_id not in self._data:
            raise BalanceNotFoundError(account_id)
        return self._data[account_id]


class MockCalendarProvider:
    def __init__(self, days: list[date]):
        self._days = days

    def get_non_working_days(self) -> list[date]:
        return self._days


class MockRulesProvider:
    def __init__(self, days: int):
        self._days = days

    def get_days_to_check_balance(self) -> int:
        return self._days


@pytest.fixture
def uow_factory(tmp_path):
    engine = build_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return lambda: UnitOfWork(factory)


@pytest.fixture
def case_input() -> CaseInput:
    return CaseInput(
        caseId="CASE_001",
        source="CLI",
        contracts=[ContractItem(contractId="ACC_001")],
        accountClosure=AccountClosure(entity="0014"),
    )


@pytest.fixture
def envelope_with_case_input(case_input) -> PipelineEnvelope:
    return PipelineEnvelope(source_file=Path("case.json"), domain_input=case_input)


@pytest.fixture
def envelope_with_domain_result() -> PipelineEnvelope:
    return PipelineEnvelope(
        correlation_id="corr-001",
        source_file=Path("case.json"),
        started_at=utc_now(),
        domain_result=DomainResult(
            case_id="CASE_001",
            action=Action.POSITIVE_BALANCE,
            date_time=None,
        ),
    )


@pytest.fixture
def persisted_pending_record(uow_factory) -> ProcessingRecordCreate:
    record = ProcessingRecordCreate(
        correlation_id="corr-001",
        case_id="CASE_001",
        source_file="case.json",
        detected_at=utc_now(),
    )
    with uow_factory() as uow:
        assert uow.records is not None
        uow.records.add(record)
    return record
