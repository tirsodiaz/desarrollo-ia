from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from check_account_balance.domain.models import CaseInput
from check_account_balance.ports.case_reader import CaseFile


class FileCaseReader:
    def __init__(self, inbox_dir: Path, processing_dir: Path, processed_dir: Path) -> None:
        self._inbox_dir = inbox_dir
        self._processing_dir = processing_dir
        self._processed_dir = processed_dir

    def read_cases(self) -> list[CaseFile]:
        case_files: list[CaseFile] = []
        for inbox_file in sorted(self._inbox_dir.glob("*.json")):
            processing_file = self._processing_dir / inbox_file.name
            shutil.move(str(inbox_file), str(processing_file))

            raw_payload = json.loads(processing_file.read_text(encoding="utf-8"))
            case_input = CaseInput.from_dict(raw_payload)
            case_id = case_input.case_id or processing_file.stem

            case_files.append(
                CaseFile(
                    case_id=case_id,
                    source_path=inbox_file,
                    processing_path=processing_file,
                    case_input=case_input,
                )
            )

        return case_files

    def cleanup(self, case_file: CaseFile) -> None:
        if case_file.processing_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = case_file.processing_path.stem
            suffix = case_file.processing_path.suffix
            dest = self._processed_dir / f"{stem}_{timestamp}{suffix}"
            shutil.move(str(case_file.processing_path), str(dest))
