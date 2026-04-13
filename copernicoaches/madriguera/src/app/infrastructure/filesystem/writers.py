from pathlib import Path

from app.domain.models import DomainResult, ErrorEntry, ErrorPayload, OutputPayload
from app.time_utils import utc_now


class OutputWriter:
    def __init__(self, outbox_dir: Path):
        self._outbox_dir = outbox_dir

    def write(self, result: DomainResult) -> Path:
        payload = OutputPayload(
            caseId=result.case_id,
            action=str(result.action),
            dateTime=result.date_time.isoformat() if result.date_time else None,
        )
        out_file = self._outbox_dir / f"{result.case_id}.json"
        out_file.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
        return out_file


class ErrorWriter:
    def __init__(self, errors_dir: Path):
        self._errors_dir = errors_dir

    def write(self, case_id: str, error_code: str, error_message: str) -> Path:
        payload = ErrorPayload(
            caseId=case_id,
            taskName="Check Account Balance",
            dateTime=utc_now().isoformat(),
            errors=[ErrorEntry(code=error_code, message=error_message)],
        )
        err_file = self._errors_dir / f"{case_id}_error.json"
        err_file.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
        return err_file
