import json
import logging
from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError

from app.application.ports import BusinessProcessor, ProcessingError, ProcessingRecordCreate
from app.domain.models import CaseInput
from app.infrastructure.filesystem.writers import ErrorWriter, OutputWriter
from app.infrastructure.persistence.uow import UnitOfWork
from app.pipeline.contracts import PipelineEnvelope, PipelineStatus

logger = logging.getLogger(__name__)


class BaseStage:
    name: str = "unnamed_stage"
    run_on_error: bool = False

    def _fail(self, envelope: PipelineEnvelope, code: str, message: str) -> PipelineEnvelope:
        envelope.status = PipelineStatus.ERROR
        envelope.failed_stage = self.name
        envelope.error_code = code
        envelope.error_message = message
        return envelope


class IngestStage(BaseStage):
    name = "ingest"

    def __init__(self, processing_dir: Path | None = None):
        self._processing_dir = processing_dir

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        if self._processing_dir is None:
            return envelope

        try:
            destination = self._processing_dir / envelope.source_file.name
            envelope.source_file.rename(destination)
            envelope.source_file = destination
            envelope.raw_content = destination.read_text(encoding="utf-8")
            return envelope
        except FileNotFoundError as exc:
            return self._fail(envelope, "ERR_INGEST_FILE_NOT_FOUND", str(exc))
        except OSError as exc:
            return self._fail(envelope, "ERR_INGEST_OS_ERROR", str(exc))

        return envelope


class ParseStage(BaseStage):
    name = "parse"

    def __init__(self, strict: bool = True):
        self._strict = strict

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        if envelope.raw_content is None:
            if not self._strict:
                return envelope
            return self._fail(envelope, "ERR_PARSE_NO_CONTENT", "raw_content is empty")

        try:
            data = json.loads(envelope.raw_content)
            envelope.domain_input = CaseInput.model_validate(data)
            return envelope
        except json.JSONDecodeError as exc:
            return self._fail(envelope, "ERR_PARSE_INVALID_JSON", str(exc))
        except ValidationError as exc:
            return self._fail(envelope, "ERR_PARSE_SCHEMA_VIOLATION", str(exc))

        return envelope


class ValidateStage(BaseStage):
    name = "validate"

    def __init__(self, strict: bool = True):
        self._strict = strict

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        case_input = envelope.domain_input
        if case_input is None:
            if not self._strict:
                return envelope
            return self._fail(envelope, "ERR_VALIDATE_NO_INPUT", "domain_input not set")
        if not isinstance(case_input, CaseInput):
            return self._fail(envelope, "ERR_VALIDATE_INVALID_INPUT", "domain_input is invalid")
        if len(case_input.contracts) == 0:
            return self._fail(
                envelope,
                "ERR_VALIDATE_NO_CONTRACTS",
                "contracts list is empty",
            )
        if not case_input.contracts[0].contractId.strip():
            return self._fail(
                envelope,
                "ERR_VALIDATE_EMPTY_CONTRACT_ID",
                "contracts[0].contractId is blank",
            )
        return envelope


class ProcessStage(BaseStage):
    name = "process"

    def __init__(self, processor: BusinessProcessor | None = None):
        self._processor = processor

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        if self._processor is None:
            return envelope

        case_input = envelope.domain_input
        if case_input is None:
            return self._fail(envelope, "ERR_PROCESS_NO_INPUT", "domain_input is None")
        if not isinstance(case_input, CaseInput):
            return self._fail(envelope, "ERR_PROCESS_INVALID_INPUT", "domain_input is invalid")

        try:
            envelope.domain_result = self._processor.process(case_input)
            return envelope
        except ProcessingError as exc:
            return self._fail(envelope, exc.code, exc.message)
        except Exception as exc:
            return self._fail(envelope, "ERR_PROCESS_UNEXPECTED", str(exc))

        return envelope


class PersistStage(BaseStage):
    name = "persist"

    def __init__(self, uow_factory: Callable[[], UnitOfWork] | None = None):
        self._uow_factory = uow_factory

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        if self._uow_factory is None:
            return envelope

        result = envelope.domain_result
        if result is None:
            return self._fail(envelope, "ERR_PERSIST_NO_RESULT", "domain_result is None")

        try:
            with self._uow_factory() as uow:
                assert uow.records is not None
                if uow.records.get_by_correlation_id(envelope.correlation_id) is None:
                    uow.records.add(
                        ProcessingRecordCreate(
                            correlation_id=envelope.correlation_id,
                            case_id=result.case_id,
                            source_file=str(envelope.source_file),
                            detected_at=envelope.detected_at,
                        )
                    )
                uow.records.update_status(
                    correlation_id=envelope.correlation_id,
                    status="PROCESSING",
                    case_id=result.case_id,
                    action=result.action,
                    started_at=envelope.started_at,
                )
            return envelope
        except Exception as exc:
            return self._fail(envelope, "ERR_PERSIST_DB_ERROR", str(exc))

        return envelope


class EmitStage(BaseStage):
    name = "emit"
    run_on_error = True

    def __init__(self, outbox_dir: Path | None = None, errors_dir: Path | None = None):
        self._output_writer = OutputWriter(outbox_dir) if outbox_dir is not None else None
        self._error_writer = ErrorWriter(errors_dir) if errors_dir is not None else None

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        if envelope.status == PipelineStatus.ERROR:
            if self._error_writer is None:
                return envelope
            case_id = (
                envelope.domain_input.caseId
                if isinstance(envelope.domain_input, CaseInput)
                else None
            )
            envelope.error_file = self._error_writer.write(
                case_id=case_id or f"UNKNOWN_{envelope.source_file.stem}",
                error_code=envelope.error_code or "ERR_UNKNOWN",
                error_message=envelope.error_message or "Unknown error",
            )
            return envelope

        if self._output_writer is None:
            return envelope

        result = envelope.domain_result
        if result is None:
            return self._fail(envelope, "ERR_EMIT_NO_RESULT", "domain_result is None")

        try:
            envelope.output_file = self._output_writer.write(result)
            return envelope
        except OSError as exc:
            return self._fail(envelope, "ERR_EMIT_WRITE_FAILED", str(exc))

        return envelope


class ArchiveStage(BaseStage):
    name = "archive"
    run_on_error = True

    def __init__(self, archive_dir: Path | None = None):
        self._archive_dir = archive_dir

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        if self._archive_dir is None:
            return envelope
        try:
            source = envelope.source_file
            if not source.exists():
                return envelope
            destination = self._archive_dir / source.name
            source.rename(destination)
            envelope.source_file = destination
            return envelope
        except OSError as exc:
            logger.warning("Failed to archive %s: %s", envelope.source_file, exc)
            return envelope

        return envelope
