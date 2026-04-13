from __future__ import annotations

from datetime import date, timedelta


def calculate_working_day(
    from_date: date,
    days_ahead: int,
    non_working_days: list[date],
) -> date:
    current = from_date
    counted = 0

    target_days = max(days_ahead, 1)

    while True:
        current = current + timedelta(days=1)
        if _is_working_day(current, non_working_days):
            counted += 1
            if counted >= target_days:
                return current


def _is_working_day(candidate: date, non_working_days: list[date]) -> bool:
    if candidate.weekday() >= 5:
        return False
    return candidate not in non_working_days
