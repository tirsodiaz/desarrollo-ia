from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.ports import ProcessingRecordCreate, ProcessingRecordRead
from app.infrastructure.persistence.models import ProcessingRecord
from app.time_utils import to_aware_utc, to_naive_utc


class SqlProcessingRecordRepository:
    def __init__(self, session: Session):
        self._session = session

    def add(self, record: ProcessingRecordCreate) -> None:
        self._session.add(
            ProcessingRecord(
                correlation_id=record.correlation_id,
                case_id=record.case_id,
                source_file=record.source_file,
                detected_at=to_naive_utc(record.detected_at),
                status=record.status,
            )
        )

    def get_by_correlation_id(self, correlation_id: str) -> ProcessingRecordRead | None:
        record = self._session.scalar(
            select(ProcessingRecord).where(
                ProcessingRecord.correlation_id == correlation_id,
            )
        )
        if record is None:
            return None
        return self._to_read_model(record)

    def update_status(self, correlation_id: str, status: str, **kwargs) -> None:
        self._session.flush()
        record = self._session.scalar(
            select(ProcessingRecord).where(
                ProcessingRecord.correlation_id == correlation_id,
            )
        )
        if record is None:
            raise LookupError(f"Processing record not found: {correlation_id}")

        record.status = status
        for field_name in (
            "action",
            "output_file",
            "error_details",
            "started_at",
            "completed_at",
            "case_id",
        ):
            if field_name in kwargs:
                value = kwargs[field_name]
                if field_name == "action" and value is not None:
                    value = str(value)
                if field_name in {"started_at", "completed_at"}:
                    value = to_naive_utc(value)
                setattr(record, field_name, value)

    def exists(self, source_file: str) -> bool:
        return self._session.scalar(
            select(ProcessingRecord.id).where(ProcessingRecord.source_file == source_file)
        ) is not None

    def get_all_for_file(self, source_file: str) -> list[ProcessingRecordRead]:
        records: Sequence[ProcessingRecord] = self._session.scalars(
            select(ProcessingRecord).where(ProcessingRecord.source_file == source_file)
        ).all()
        return [self._to_read_model(record) for record in records]

    @staticmethod
    def _to_read_model(record: ProcessingRecord) -> ProcessingRecordRead:
        return ProcessingRecordRead(
            correlation_id=record.correlation_id,
            case_id=record.case_id,
            source_file=record.source_file,
            detected_at=to_aware_utc(record.detected_at),
            status=record.status,
            action=record.action,
            output_file=record.output_file,
            error_details=record.error_details,
        )
