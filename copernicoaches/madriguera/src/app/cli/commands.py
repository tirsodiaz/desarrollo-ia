import logging
import time
from collections.abc import Iterable
from pathlib import Path

import structlog
import typer

from app.application.services import FileProcessingService
from app.config.settings import AppSettings
from app.infrastructure.persistence.session import build_session_factory, create_all_tables
from app.infrastructure.persistence.uow import UnitOfWork
from app.infrastructure.watcher.file_watcher import FileWatcher
from app.pipeline.engine import build_pipeline

app = typer.Typer(help="Madriguera file-driven processing runtime.")


@app.callback()
def main() -> None:
    """CLI entry point for Madriguera."""


def _coerce_log_level(log_level: str) -> int:
    return getattr(logging, log_level.upper(), logging.INFO)


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        format="%(message)s",
        level=_coerce_log_level(log_level),
        force=True,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def ensure_directories(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


@app.command()
def run() -> None:
    settings = AppSettings()
    configure_logging(settings.log_level)
    logger = structlog.get_logger("madriguera")

    ensure_directories(settings.runtime_directories())
    session_factory = build_session_factory(settings.database_url)
    session = session_factory()
    bind = session.bind
    session.close()
    if bind is None:
        raise RuntimeError("Session factory is not bound to an engine")
    create_all_tables(bind)

    uow_factory = lambda: UnitOfWork(session_factory)
    pipeline = build_pipeline(settings=settings)
    service = FileProcessingService(pipeline=pipeline, uow_factory=uow_factory)
    watcher = FileWatcher(
        inbox_dir=settings.inbox_dir,
        on_file_ready=service.handle,
        stabilisation_seconds=settings.file_stabilisation_seconds,
    )

    logger.info(f"Madriguera started. Watching: {settings.inbox_dir}")
    watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        logger.info("Madriguera stopped.")
