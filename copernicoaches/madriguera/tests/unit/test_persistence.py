from datetime import UTC

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.application.ports import ProcessingRecordCreate
from app.infrastructure.persistence.models import Base, ProcessingRecord
from app.infrastructure.persistence.session import build_engine
from app.infrastructure.persistence.uow import UnitOfWork
from app.time_utils import utc_now


@pytest.fixture
def uow_factory(tmp_path):
    engine = build_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    return lambda: UnitOfWork(session_factory)


def test_add_and_retrieve(uow_factory) -> None:
    with uow_factory() as uow:
        assert uow.records is not None
        uow.records.add(
            ProcessingRecordCreate(
                correlation_id="corr-001",
                case_id="CASE_001",
                source_file="inbox/case_001.json",
                detected_at=utc_now(),
            )
        )

    with uow_factory() as uow:
        assert uow.records is not None
        record = uow.records.get_by_correlation_id("corr-001")
        assert record is not None
        assert record.case_id == "CASE_001"
        assert record.status == "PENDING"
        assert record.detected_at.tzinfo is UTC


def test_update_status_changes_status_and_optional_fields(uow_factory) -> None:
    detected_at = utc_now()
    completed_at = utc_now()

    with uow_factory() as uow:
        assert uow.records is not None
        uow.records.add(
            ProcessingRecordCreate(
                correlation_id="corr-001",
                case_id="CASE_001",
                source_file="inbox/case_001.json",
                detected_at=detected_at,
            )
        )

    with uow_factory() as uow:
        assert uow.records is not None
        uow.records.update_status(
            "corr-001",
            "SUCCESS",
            action="positiveBalance",
            output_file="outbox/case_001.json",
            completed_at=completed_at,
        )

    with uow_factory() as uow:
        assert uow.records is not None
        record = uow.records.get_by_correlation_id("corr-001")
        assert record is not None
        assert record.status == "SUCCESS"
        assert record.action == "positiveBalance"


def test_exists_returns_true_for_known_file_and_false_for_unknown(uow_factory) -> None:
    with uow_factory() as uow:
        assert uow.records is not None
        uow.records.add(
            ProcessingRecordCreate(
                correlation_id="corr-001",
                case_id="CASE_001",
                source_file="inbox/case_001.json",
                detected_at=utc_now(),
            )
        )

    with uow_factory() as uow:
        assert uow.records is not None
        assert uow.records.exists("inbox/case_001.json") is True
        assert uow.records.exists("inbox/never_seen.json") is False


def test_rollback_on_exception(uow_factory) -> None:
    with pytest.raises(RuntimeError):
        with uow_factory() as uow:
            assert uow.records is not None
            uow.records.add(
                ProcessingRecordCreate(
                    correlation_id="corr-002",
                    case_id="X",
                    source_file="f.json",
                    detected_at=utc_now(),
                )
            )
            raise RuntimeError("simulated failure")

    with uow_factory() as uow:
        assert uow.records is not None
        assert uow.records.get_by_correlation_id("corr-002") is None


def test_duplicate_correlation_id_raises_integrity_error(uow_factory) -> None:
    with uow_factory() as uow:
        assert uow.records is not None
        uow.records.add(
            ProcessingRecordCreate(
                correlation_id="corr-001",
                case_id="CASE_001",
                source_file="inbox/case_001.json",
                detected_at=utc_now(),
            )
        )

    with pytest.raises(IntegrityError):
        with uow_factory() as uow:
            assert uow.records is not None
            uow.records.add(
                ProcessingRecordCreate(
                    correlation_id="corr-001",
                    case_id="CASE_002",
                    source_file="inbox/case_002.json",
                    detected_at=utc_now(),
                )
            )


def test_repository_reads_aware_utc_and_stores_naive_utc(tmp_path) -> None:
    engine = build_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    detected_at = utc_now()

    with UnitOfWork(session_factory) as uow:
        assert uow.records is not None
        uow.records.add(
            ProcessingRecordCreate(
                correlation_id="corr-utc",
                case_id="CASE_UTC",
                source_file="inbox/case_utc.json",
                detected_at=detected_at,
            )
        )

    with session_factory() as session:
        record = session.query(ProcessingRecord).filter_by(correlation_id="corr-utc").one()
        assert record.detected_at.tzinfo is None

    with UnitOfWork(session_factory) as uow:
        assert uow.records is not None
        record = uow.records.get_by_correlation_id("corr-utc")
        assert record is not None
        assert record.detected_at.tzinfo is UTC
        assert record.detected_at == detected_at
