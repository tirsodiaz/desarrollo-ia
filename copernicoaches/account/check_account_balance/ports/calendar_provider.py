from __future__ import annotations

from datetime import date
from typing import Protocol


class CalendarProvider(Protocol):
    def get_non_working_days(self) -> list[date]: ...
