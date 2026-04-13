from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from app.domain.models import CaseInput, DomainResult


class BalanceNotFoundError(Exception):
    def __init__(self, account_id: str):
        super().__init__(f"Balance not found for account: {account_id}")
        self.account_id = account_id


class BalanceProvider(Protocol):
    def get_balance(self, account_id: str) -> float:
        """Raises BalanceNotFoundError if account_id is unknown."""


class CalendarProvider(Protocol):
    def get_non_working_days(self) -> list[date]:
        """Returns configured non-working days excluding weekends."""


class RulesProvider(Protocol):
    def get_days_to_check_balance(self) -> int:
        """Returns the number of working days used to calculate the check date."""


@dataclass(slots=True)
class ProcessingRecordCreate:
    correlation_id: str
    case_id: str
    source_file: str
    detected_at: datetime
    status: str = "PENDING"


@dataclass(slots=True)
class ProcessingRecordRead:
    correlation_id: str
    case_id: str
    source_file: str
    detected_at: datetime
    status: str
    action: str | None
    output_file: str | None
    error_details: str | None


class ProcessingRecordRepository(Protocol):
    def add(self, record: ProcessingRecordCreate) -> None: ...

    def get_by_correlation_id(
        self,
        correlation_id: str,
    ) -> ProcessingRecordRead | None: ...

    def update_status(self, correlation_id: str, status: str, **kwargs) -> None: ...

    def exists(self, source_file: str) -> bool: ...


class ProcessingError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class BusinessProcessor(Protocol):
    def process(self, case_input: CaseInput) -> DomainResult:
        """Apply business rules and return a DomainResult."""
