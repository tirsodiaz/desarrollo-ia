from __future__ import annotations

from typing import Protocol

from check_account_balance.domain.models import DomainResult


class ResultWriter(Protocol):
    def write_result(self, result: DomainResult) -> None: ...

    def write_error(self, case_id: str, code: str, message: str) -> None: ...
