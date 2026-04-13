from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from check_account_balance.domain.models import CaseInput


@dataclass(frozen=True)
class CaseFile:
    case_id: str
    source_path: Path
    processing_path: Path
    case_input: CaseInput


class CaseReader(Protocol):
    def read_cases(self) -> list[CaseFile]: ...

    def cleanup(self, case_file: CaseFile) -> None: ...
