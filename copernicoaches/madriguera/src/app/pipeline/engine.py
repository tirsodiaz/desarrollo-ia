import logging
from collections.abc import Callable
from datetime import date

from app.application.check_balance_processor import CheckAccountBalanceProcessor
from app.config.settings import AppSettings
from app.infrastructure.filesystem.config_readers import (
    FileBalanceProvider,
    FileCalendarProvider,
    FileRulesProvider,
)
from app.infrastructure.persistence.session import build_session_factory
from app.infrastructure.persistence.uow import UnitOfWork
from app.pipeline.contracts import PipelineEnvelope, PipelineStage, PipelineStatus
from app.pipeline.stages import (
    ArchiveStage,
    EmitStage,
    IngestStage,
    ParseStage,
    PersistStage,
    ProcessStage,
    ValidateStage,
)
from app.time_utils import utc_now

logger = logging.getLogger(__name__)


class PipelineEngine:
    def __init__(self, stages: list[PipelineStage]):
        self._stages = stages

    def run(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        envelope.status = PipelineStatus.RUNNING
        envelope.started_at = utc_now()
        error_logged = False

        for stage in self._stages:
            if envelope.status == PipelineStatus.ERROR and not getattr(stage, "run_on_error", False):
                continue

            logger.debug(
                "Stage starting",
                extra={"stage": stage.name, "correlation_id": envelope.correlation_id},
            )
            envelope = stage.execute(envelope)

            if envelope.status == PipelineStatus.ERROR:
                if not error_logged:
                    logger.error(
                        "Stage failed",
                        extra={
                            "stage": envelope.failed_stage,
                            "error": envelope.error_message,
                            "correlation_id": envelope.correlation_id,
                        },
                    )
                    error_logged = True
                continue

            logger.debug(
                "Stage completed",
                extra={"stage": stage.name, "correlation_id": envelope.correlation_id},
            )

        if envelope.status != PipelineStatus.ERROR:
            envelope.status = PipelineStatus.SUCCESS
        envelope.completed_at = utc_now()
        return envelope


def build_pipeline(
    settings: AppSettings | None = None,
    today_provider: Callable[[], date] | None = None,
) -> PipelineEngine:
    if settings is None:
        stages = [
            IngestStage(),
            ParseStage(strict=False),
            ValidateStage(strict=False),
            ProcessStage(),
            PersistStage(),
            EmitStage(),
            ArchiveStage(),
        ]
        return PipelineEngine(stages)

    balance_provider = FileBalanceProvider(settings.config_dir)
    calendar_provider = FileCalendarProvider(settings.config_dir)
    rules_provider = FileRulesProvider(settings.config_dir)
    processor = CheckAccountBalanceProcessor(
        balance_provider=balance_provider,
        calendar_provider=calendar_provider,
        rules_provider=rules_provider,
        today_provider=today_provider or date.today,
    )
    session_factory = build_session_factory(settings.database_url)
    uow_factory = lambda: UnitOfWork(session_factory)

    stages = [
        IngestStage(processing_dir=settings.processing_dir),
        ParseStage(strict=True),
        ValidateStage(strict=True),
        ProcessStage(processor=processor),
        PersistStage(uow_factory=uow_factory),
        EmitStage(outbox_dir=settings.outbox_dir, errors_dir=settings.errors_dir),
        ArchiveStage(archive_dir=settings.archive_dir),
    ]
    return PipelineEngine(stages)
