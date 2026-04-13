from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from check_account_balance.domain.models import DomainResult


class FileResultWriter:
    def __init__(self, outbox_dir: Path, errors_dir: Path) -> None:
        self._outbox_dir = outbox_dir
        self._errors_dir = errors_dir

    def write_result(self, result: DomainResult) -> None:
        payload = {
            "caseId": result.case_id,
            "action": result.action.value,
            "dateTime": result.date_time.isoformat() if result.date_time else None,
        }
        file_path = self._outbox_dir / f"{result.case_id}.json"
        file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def write_error(self, case_id: str, code: str, message: str) -> None:
        payload = {
            "caseId": case_id,
            "taskName": "Check Account Balance",
            "dateTime": datetime.now().isoformat(timespec="seconds"),
            "errors": [{"code": code, "message": message}],
        }
        file_path = self._errors_dir / f"{case_id}_error.json"
        file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
