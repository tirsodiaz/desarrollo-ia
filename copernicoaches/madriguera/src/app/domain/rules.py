from datetime import date, datetime, time, timedelta
from typing import Callable

from app.domain.models import Action, CaseInput, DomainResult


def _at_processing_time(value: date) -> datetime:
    return datetime.combine(value, time(0, 1, 0))


def decide_action(
    case_input: CaseInput,
    balance: float,
    today: date,
    working_day_calculator: Callable[[date, int, list[date]], date],
    non_working_days: list[date],
    days_to_check: int,
) -> DomainResult:
    if balance > 0:
        return DomainResult(case_id=case_input.caseId, action=Action.POSITIVE_BALANCE)

    if balance == 0:
        return DomainResult(case_id=case_input.caseId, action=Action.ZERO_BALANCE)

    if case_input.source == "CLI":
        _sub_action = Action.CUSTOMER_NEGATIVE_BALANCE
    else:
        _sub_action = Action.BANK_NEGATIVE_BALANCE

    date_to_check = case_input.accountClosure.dateToCheckBalance
    if date_to_check is None:
        calculated_date = working_day_calculator(today, days_to_check, non_working_days)
        return DomainResult(
            case_id=case_input.caseId,
            action=Action.WAIT,
            date_time=_at_processing_time(calculated_date),
        )

    if date_to_check == today:
        return DomainResult(case_id=case_input.caseId, action=Action.CANCEL)

    return DomainResult(
        case_id=case_input.caseId,
        action=Action.WAIT,
        date_time=_at_processing_time(date_to_check),
    )


def calculate_working_day(
    from_date: date,
    days_ahead: int,
    non_working_days: list[date],
) -> date:
    if days_ahead < 0:
        raise ValueError("days_ahead must be >= 0")

    candidate = from_date
    counted_working_days = 0
    holidays = set(non_working_days)

    while counted_working_days < days_ahead:
        candidate += timedelta(days=1)
        if candidate.weekday() >= 5 or candidate in holidays:
            continue
        counted_working_days += 1

    if days_ahead == 0:
        candidate += timedelta(days=1)
        while candidate.weekday() >= 5 or candidate in holidays:
            candidate += timedelta(days=1)

    return candidate
