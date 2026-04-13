import json
from datetime import date
from pathlib import Path

import pytest

from app.application.ports import (
    BalanceNotFoundError,
    BalanceProvider,
    CalendarProvider,
    RulesProvider,
)
from app.domain.models import CaseInput
from app.infrastructure.filesystem.config_readers import (
    FileBalanceProvider,
    FileCalendarProvider,
    FileRulesProvider,
)


def test_balance_found() -> None:
    provider = FileBalanceProvider(Path("data/config"))

    assert provider.get_balance("ACC_001") == 120.50


def test_balance_not_found_raises_balance_not_found_error() -> None:
    provider = FileBalanceProvider(Path("data/config"))

    with pytest.raises(BalanceNotFoundError) as exc_info:
        provider.get_balance("UNKNOWN")

    assert exc_info.value.account_id == "UNKNOWN"


def test_calendar_returns_parsed_dates() -> None:
    provider = FileCalendarProvider(Path("tests/fixtures/config"))

    days = provider.get_non_working_days()

    assert date(2026, 3, 23) in days


def test_rules_returns_integer() -> None:
    provider = FileRulesProvider(Path("data/config"))

    assert provider.get_days_to_check_balance() == 3


def test_missing_config_file_raises_file_not_found_error() -> None:
    provider = FileBalanceProvider(Path("/nonexistent"))

    with pytest.raises(FileNotFoundError):
        provider.get_balance("ACC_001")


def test_file_providers_satisfy_protocol_interfaces() -> None:
    balance_provider: BalanceProvider = FileBalanceProvider(Path("data/config"))
    calendar_provider: CalendarProvider = FileCalendarProvider(Path("data/config"))
    rules_provider: RulesProvider = FileRulesProvider(Path("data/config"))

    assert balance_provider.get_balance("ACC_002") == 0.0
    assert calendar_provider.get_non_working_days() == []
    assert rules_provider.get_days_to_check_balance() == 3


def test_sample_inbox_files_are_valid_case_input() -> None:
    for path in Path("data/inbox").glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        case = CaseInput.model_validate(payload)
        assert case.caseId is not None
