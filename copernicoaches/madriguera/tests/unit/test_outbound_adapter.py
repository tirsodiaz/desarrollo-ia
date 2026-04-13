import json
import shutil
from datetime import date, datetime
from pathlib import Path

from app.application.services import FileProcessingService
from app.config.settings import AppSettings
from app.domain.models import Action, DomainResult
from app.infrastructure.filesystem.writers import ErrorWriter, OutputWriter
from app.infrastructure.persistence.session import build_engine, build_session_factory, create_all_tables
from app.infrastructure.persistence.uow import UnitOfWork
from app.pipeline.contracts import PipelineEnvelope, PipelineStatus
from app.pipeline.engine import build_pipeline
from app.pipeline.stages import ArchiveStage, EmitStage


def test_output_writer_positive(tmp_path) -> None:
    writer = OutputWriter(tmp_path)
    result = DomainResult(case_id="CASE_001", action=Action.POSITIVE_BALANCE, date_time=None)

    out_file = writer.write(result)

    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["caseId"] == "CASE_001"
    assert data["action"] == "positiveBalance"
    assert data["dateTime"] is None


def test_output_writer_wait(tmp_path) -> None:
    writer = OutputWriter(tmp_path)
    result = DomainResult(
        case_id="CASE_003",
        action=Action.WAIT,
        date_time=datetime(2026, 3, 25, 0, 1, 0),
    )

    out_file = writer.write(result)
    data = json.loads(out_file.read_text(encoding="utf-8"))

    assert data["action"] == "wait"
    assert data["dateTime"] == "2026-03-25T00:01:00"


def test_error_writer(tmp_path) -> None:
    writer = ErrorWriter(tmp_path)

    out_file = writer.write("CASE_001", "ERR_BALANCE_NOT_FOUND", "Balance not found")

    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["caseId"] == "CASE_001"
    assert data["taskName"] == "Check Account Balance"
    assert data["dateTime"].endswith("+00:00")
    assert len(data["errors"]) == 1
    assert data["errors"][0]["code"] == "ERR_BALANCE_NOT_FOUND"


def test_emit_stage_success(tmp_path, envelope_with_domain_result) -> None:
    outbox = tmp_path / "outbox"
    errors = tmp_path / "errors"
    outbox.mkdir()
    errors.mkdir()

    result = EmitStage(outbox_dir=outbox, errors_dir=errors).execute(envelope_with_domain_result)

    assert result.output_file is not None
    assert result.output_file.exists()


def test_emit_stage_error_path(tmp_path) -> None:
    outbox = tmp_path / "outbox"
    errors = tmp_path / "errors"
    outbox.mkdir()
    errors.mkdir()

    envelope = PipelineEnvelope(source_file=Path("inbox/case.json"))
    envelope.status = PipelineStatus.ERROR
    envelope.error_code = "ERR_TEST"
    envelope.error_message = "test error"
    envelope.failed_stage = "parse"

    result = EmitStage(outbox_dir=outbox, errors_dir=errors).execute(envelope)

    assert result.error_file is not None
    assert result.error_file.exists()
    assert result.status == PipelineStatus.ERROR


def test_archive_stage(tmp_path) -> None:
    processing = tmp_path / "processing"
    archive = tmp_path / "archive"
    processing.mkdir()
    archive.mkdir()
    source = processing / "case_001.json"
    source.write_text("{}", encoding="utf-8")
    envelope = PipelineEnvelope(source_file=source)

    result = ArchiveStage(archive_dir=archive).execute(envelope)

    assert not source.exists()
    assert (archive / "case_001.json").exists()
    assert result.status != PipelineStatus.ERROR


def test_end_to_end_all_scenarios(tmp_path) -> None:
    settings = _prepare_runtime(tmp_path)
    pipeline = build_pipeline(settings, today_provider=lambda: date(2026, 3, 20))
    service = FileProcessingService(
        pipeline=pipeline,
        uow_factory=lambda: UnitOfWork(build_session_factory(settings.database_url)),
    )

    expected = {
        "case_positive.json": ("CASE_001", "positiveBalance"),
        "case_zero.json": ("CASE_002", "zeroBalance"),
        "case_neg_cli.json": ("CASE_003", "wait"),
        "case_neg_bank.json": ("CASE_004", "wait"),
        "case_wait.json": ("CASE_005", "wait"),
        "case_cancel.json": ("CASE_006", "cancel"),
    }

    for file_name, (case_id, action) in expected.items():
        destination = settings.inbox_dir / file_name
        shutil.copy2(Path("data/inbox") / file_name, destination)
        service.handle(destination)

        out_file = settings.outbox_dir / f"{case_id}.json"
        assert out_file.exists()
        payload = json.loads(out_file.read_text(encoding="utf-8"))
        assert payload["action"] == action
        if action == "wait":
            assert payload["dateTime"] is not None


def test_end_to_end_unknown_account_produces_error_file(tmp_path) -> None:
    settings = _prepare_runtime(tmp_path)
    pipeline = build_pipeline(settings, today_provider=lambda: date(2026, 3, 20))
    session_factory = build_session_factory(settings.database_url)
    service = FileProcessingService(
        pipeline=pipeline,
        uow_factory=lambda: UnitOfWork(session_factory),
    )

    source = settings.inbox_dir / "case_unknown.json"
    source.write_text(
        json.dumps(
            {
                "caseId": "CASE_UNKNOWN",
                "source": "CLI",
                "contracts": [{"contractId": "ACC_UNKNOWN"}],
                "accountClosure": {"dateToCheckBalance": None, "entity": "0014"},
            }
        ),
        encoding="utf-8",
    )

    service.handle(source)

    assert not (settings.outbox_dir / "CASE_UNKNOWN.json").exists()
    error_file = settings.errors_dir / "CASE_UNKNOWN_error.json"
    assert error_file.exists()
    payload = json.loads(error_file.read_text(encoding="utf-8"))
    assert payload["errors"][0]["code"] == "ERR_BALANCE_NOT_FOUND"

    with UnitOfWork(session_factory) as uow:
        assert uow.records is not None
        records = uow.records.get_all_for_file(str(source))
        assert len(records) == 1
        assert records[0].status == "ERROR"


def _prepare_runtime(tmp_path) -> AppSettings:
    for name in ("inbox", "processing", "outbox", "errors", "archive", "config"):
        (tmp_path / name).mkdir()

    shutil.copy2(Path("data/config") / "balances.json", tmp_path / "config" / "balances.json")
    shutil.copy2(Path("data/config") / "calendar.json", tmp_path / "config" / "calendar.json")
    shutil.copy2(Path("data/config") / "rules.json", tmp_path / "config" / "rules.json")

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
    return settings
