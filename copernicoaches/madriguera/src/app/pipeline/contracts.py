from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Protocol
import uuid

from pydantic import BaseModel, Field
from app.time_utils import utc_now


class PipelineStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class PipelineEnvelope(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file: Path

    detected_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: PipelineStatus = PipelineStatus.PENDING

    raw_content: str | None = None
    domain_input: object | None = None
    domain_result: object | None = None
    output_file: Path | None = None
    error_file: Path | None = None

    failed_stage: str | None = None
    error_message: str | None = None
    error_code: str | None = None


class PipelineStage(Protocol):
    name: str

    def execute(self, envelope: PipelineEnvelope) -> PipelineEnvelope:
        """Execute the stage and return the updated envelope."""
