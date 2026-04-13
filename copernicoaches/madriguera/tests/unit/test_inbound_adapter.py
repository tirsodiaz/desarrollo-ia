import json
import threading
import time
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

from app.application.ports import ProcessingRecordCreate
from app.application.services import FileProcessingService
from app.domain.models import AccountClosure, CaseInput, ContractItem
from app.infrastructure.persistence.models import Base
from app.infrastructure.persistence.session import build_engine
from app.infrastructure.persistence.uow import UnitOfWork
from app.infrastructure.watcher.file_watcher import FileWatcher
from app.pipeline.contracts import PipelineEnvelope, PipelineStatus
from app.pipeline.stages import IngestStage, ParseStage, ValidateStage
from app.time_utils import utc_now


class StubPipeline:
    def run(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        envelope.status = PipelineStatus.SUCCESS
        envelope.completed_at = utc_now()
        return envelope


@pytest.fixture
def uow_factory(tmp_path):
    engine = build_engine(f"sqlite:///{tmp_path}/test.db")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return lambda: UnitOfWork(factory)


@pytest.fixture
def valid_case_json() -> str:
    return json.dumps(
        {
            "caseId": "CASE_001",
            "source": "CLI",
            "contracts": [{"contractId": "ACC_001"}],
            "accountClosure": {"dateToCheckBalance": None, "entity": "0014"},
        }
    )


def test_ingest_stage_moves_file(tmp_path) -> None:
    inbox = tmp_path / "inbox"
    processing = tmp_path / "processing"
    inbox.mkdir()
    processing.mkdir()

    test_file = inbox / "case_001.json"
    test_file.write_text('{"caseId": "X"}', encoding="utf-8")

    stage = IngestStage(processing_dir=processing)
    envelope = PipelineEnvelope(source_file=test_file)

    result = stage.execute(envelope)

    assert result.status != PipelineStatus.ERROR
    assert (processing / "case_001.json").exists()
    assert not test_file.exists()
    assert result.raw_content == '{"caseId": "X"}'


def test_ingest_stage_missing_file(tmp_path) -> None:
    stage = IngestStage(processing_dir=tmp_path)
    envelope = PipelineEnvelope(source_file=Path("/nonexistent/file.json"))

    result = stage.execute(envelope)

    assert result.status == PipelineStatus.ERROR
    assert result.error_code == "ERR_INGEST_FILE_NOT_FOUND"


def test_parse_stage_valid_json(valid_case_json) -> None:
    stage = ParseStage()
    envelope = PipelineEnvelope(source_file=Path("x.json"), raw_content=valid_case_json)

    result = stage.execute(envelope)

    assert result.status != PipelineStatus.ERROR
    assert isinstance(result.domain_input, CaseInput)
    assert result.domain_input.caseId == "CASE_001"


def test_parse_stage_bad_json() -> None:
    stage = ParseStage()
    envelope = PipelineEnvelope(source_file=Path("x.json"), raw_content="{not json}")

    result = stage.execute(envelope)

    assert result.status == PipelineStatus.ERROR
    assert result.error_code == "ERR_PARSE_INVALID_JSON"


def test_validate_empty_contracts() -> None:
    case = CaseInput.model_construct(
        caseId="X",
        source="CLI",
        contracts=[],
        accountClosure=AccountClosure(entity="0014"),
    )
    envelope = PipelineEnvelope(source_file=Path("x.json"), domain_input=case)

    result = ValidateStage().execute(envelope)

    assert result.status == PipelineStatus.ERROR
    assert result.error_code == "ERR_VALIDATE_NO_CONTRACTS"


def test_idempotency(tmp_path, uow_factory, valid_case_json) -> None:
    service = FileProcessingService(pipeline=StubPipeline(), uow_factory=uow_factory)
    source_file = tmp_path / "test.json"
    source_file.write_text(valid_case_json, encoding="utf-8")

    service.handle(source_file)
    source_file.write_text(valid_case_json, encoding="utf-8")
    service.handle(source_file)

    with uow_factory() as uow:
        assert uow.records is not None
        records = uow.records.get_all_for_file(str(source_file))
        assert len(records) == 1


def test_watcher_detects_json(tmp_path) -> None:
    received: list[Path] = []
    ready = threading.Event()

    watcher = FileWatcher(
        inbox_dir=tmp_path,
        on_file_ready=lambda path: (received.append(path), ready.set()),
        stabilisation_seconds=0.1,
    )
    watcher.start()
    try:
        (tmp_path / "test.json").write_text("{}", encoding="utf-8")
        assert ready.wait(timeout=3), "watcher did not detect JSON file in time"
        time.sleep(0.2)
    finally:
        watcher.stop()

    assert any(path.name == "test.json" for path in received)
