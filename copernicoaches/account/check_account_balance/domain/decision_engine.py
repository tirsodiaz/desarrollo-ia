from __future__ import annotations

from datetime import date, datetime

from check_account_balance.domain.models import Action, CaseInput, DomainResult
from check_account_balance.domain.working_day_calculator import calculate_working_day


def decide_action(
    case_input: CaseInput,
    balance: float,
    today: date,
    non_working_days: list[date],
    days_to_check: int,
) -> DomainResult:
    if balance > 0:
        return DomainResult(case_id=case_input.case_id, action=Action.POSITIVE_BALANCE)

    if balance == 0:
        return DomainResult(case_id=case_input.case_id, action=Action.ZERO_BALANCE)

    if case_input.source.strip().upper() != "CLI":
        return DomainResult(case_id=case_input.case_id, action=Action.BANK_NEGATIVE_BALANCE)

    date_to_check = case_input.account_closure.date_to_check_balance

    if date_to_check is None:
        future_date = calculate_working_day(today, days_to_check, non_working_days)
        return DomainResult(
            case_id=case_input.case_id,
            action=Action.WAIT,
            date_time=datetime(future_date.year, future_date.month, future_date.day, 0, 1),
        )

    if date_to_check == today:
        return DomainResult(case_id=case_input.case_id, action=Action.CANCEL)

    return DomainResult(
        case_id=case_input.case_id,
        action=Action.WAIT,
        date_time=datetime(date_to_check.year, date_to_check.month, date_to_check.day, 0, 1),
    )
