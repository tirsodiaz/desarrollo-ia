import logging
import uuid
from collections.abc import Callable
from pathlib import Path

from app.application.ports import ProcessingRecordCreate
from app.infrastructure.persistence.uow import UnitOfWork
from app.pipeline.engine import PipelineEngine
from app.pipeline.contracts import PipelineEnvelope
from app.pipeline.contracts import PipelineStatus

logger = logging.getLogger(__name__)


class FileProcessingService:
    def __init__(
        self,
        pipeline: PipelineEngine,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self._pipeline = pipeline
        self._uow_factory = uow_factory

    def handle(self, source_file: Path) -> None:
        correlation_id = str(uuid.uuid4())
        envelope = PipelineEnvelope(source_file=source_file, correlation_id=correlation_id)

        with self._uow_factory() as uow:
            assert uow.records is not None
            if uow.records.exists(str(source_file)):
                logger.warning("Skipping already-processed file: %s", source_file.name)
                return

            uow.records.add(
                ProcessingRecordCreate(
                    correlation_id=correlation_id,
                    case_id="UNKNOWN",
                    source_file=str(source_file),
                    detected_at=envelope.detected_at,
                    status="PENDING",
                )
            )

        result = self._pipeline.run(envelope)
        case_id = (
            getattr(result.domain_input, "caseId", None)
            or getattr(result.domain_result, "case_id", None)
            or "UNKNOWN"
        )

        with self._uow_factory() as uow:
            assert uow.records is not None
            uow.records.update_status(
                result.correlation_id,
                "SUCCESS" if result.status == PipelineStatus.SUCCESS else "ERROR",
                case_id=case_id,
                action=getattr(result.domain_result, "action", None),
                output_file=str(result.output_file) if result.output_file else None,
                error_details=result.error_message,
                completed_at=result.completed_at,
            )
