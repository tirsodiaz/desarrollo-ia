import json
from datetime import date
from pathlib import Path

from app.application.ports import BalanceNotFoundError


class FileBalanceProvider:
    def __init__(self, config_dir: Path):
        self._path = config_dir / "balances.json"

    def get_balance(self, account_id: str) -> float:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        if account_id not in data:
            raise BalanceNotFoundError(account_id)
        return float(data[account_id])


class FileCalendarProvider:
    def __init__(self, config_dir: Path):
        self._path = config_dir / "calendar.json"

    def get_non_working_days(self) -> list[date]:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return [date.fromisoformat(value) for value in data.get("non_working_days", [])]


class FileRulesProvider:
    def __init__(self, config_dir: Path):
        self._path = config_dir / "rules.json"

    def get_days_to_check_balance(self) -> int:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return int(data["daysToCheckBalance"])
