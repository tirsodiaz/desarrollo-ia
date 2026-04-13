from datetime import date, time

import pytest
from pydantic import ValidationError

from app.domain.models import AccountClosure, Action, CaseInput, ContractItem
from app.domain.rules import calculate_working_day, decide_action


def make_case_input(
    *,
    source: str = "CLI",
    date_to_check_balance: date | None = None,
) -> CaseInput:
    return CaseInput(
        caseId="CASE-001",
        source=source,
        contracts=[ContractItem(contractId="ACC-123")],
        accountClosure=AccountClosure(
            dateToCheckBalance=date_to_check_balance,
            entity="0014",
        ),
    )


def test_positive_balance_returns_positive_balance_action() -> None:
    result = decide_action(
        make_case_input(),
        balance=120.50,
        today=date(2026, 3, 20),
        working_day_calculator=calculate_working_day,
        non_working_days=[],
        days_to_check=3,
    )

    assert result.action == Action.POSITIVE_BALANCE
    assert result.date_time is None


def test_zero_balance_returns_zero_balance_action() -> None:
    result = decide_action(
        make_case_input(),
        balance=0.0,
        today=date(2026, 3, 20),
        working_day_calculator=calculate_working_day,
        non_working_days=[],
        days_to_check=3,
    )

    assert result.action == Action.ZERO_BALANCE
    assert result.date_time is None


def test_negative_cli_without_existing_date_waits_for_calculated_working_day() -> None:
    result = decide_action(
        make_case_input(source="CLI", date_to_check_balance=None),
        balance=-45.0,
        today=date(2026, 3, 20),
        working_day_calculator=calculate_working_day,
        non_working_days=[],
        days_to_check=3,
    )

    assert result.action == Action.WAIT
    assert result.date_time is not None
    assert result.date_time.date() == date(2026, 3, 25)
    assert result.date_time.time() == time(0, 1, 0)


def test_negative_non_cli_with_today_date_cancels() -> None:
    result = decide_action(
        make_case_input(source="BANK", date_to_check_balance=date(2026, 3, 20)),
        balance=-10.0,
        today=date(2026, 3, 20),
        working_day_calculator=calculate_working_day,
        non_working_days=[],
        days_to_check=3,
    )

    assert result.action == Action.CANCEL
    assert result.date_time is None


def test_negative_with_existing_future_date_waits_until_that_date() -> None:
    result = decide_action(
        make_case_input(source="BANK", date_to_check_balance=date(2026, 3, 25)),
        balance=-10.0,
        today=date(2026, 3, 20),
        working_day_calculator=calculate_working_day,
        non_working_days=[],
        days_to_check=3,
    )

    assert result.action == Action.WAIT
    assert result.date_time is not None
    assert result.date_time.date() == date(2026, 3, 25)
    assert result.date_time.time() == time(0, 1, 0)


def test_working_day_calculator_skips_weekends() -> None:
    result = calculate_working_day(date(2026, 3, 20), days_ahead=1, non_working_days=[])

    assert result == date(2026, 3, 23)


def test_working_day_calculator_skips_holidays() -> None:
    holiday = date(2026, 3, 23)

    result = calculate_working_day(
        date(2026, 3, 20),
        days_ahead=1,
        non_working_days=[holiday],
    )

    assert result == date(2026, 3, 24)


def test_case_input_rejects_missing_case_id() -> None:
    with pytest.raises(ValidationError):
        CaseInput(
            source="CLI",
            contracts=[ContractItem(contractId="ACC-123")],
            accountClosure=AccountClosure(entity="0014"),
        )


def test_case_input_rejects_empty_contracts() -> None:
    with pytest.raises(ValidationError):
        CaseInput(
            caseId="CASE-001",
            source="CLI",
            contracts=[],
            accountClosure=AccountClosure(entity="0014"),
        )


def test_action_enum_serializes_to_expected_strings() -> None:
    assert Action.POSITIVE_BALANCE == "positiveBalance"
    assert Action.CUSTOMER_NEGATIVE_BALANCE == "customerNegativeBalance"
