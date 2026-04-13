from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from check_account_balance.ports.balance_provider import BalanceNotFoundError


class FileBalanceProvider:
    def __init__(self, config_dir: Path) -> None:
        self._path = config_dir / "balances.json"

    def get_balance(self, account_id: str) -> float:
        data = self._load()
        if account_id not in data:
            raise BalanceNotFoundError(account_id)
        return float(data[account_id])

    def _load(self) -> dict:
        with self._path.open(encoding="utf-8") as handle:
            return json.load(handle)


class FileCalendarProvider:
    def __init__(self, config_dir: Path) -> None:
        self._path = config_dir / "calendar.json"

    def get_non_working_days(self) -> list[date]:
        data = self._load()
        return [date.fromisoformat(item) for item in data.get("non_working_days", [])]

    def _load(self) -> dict:
        with self._path.open(encoding="utf-8") as handle:
            return json.load(handle)


class FileConfigProvider:
    def __init__(self, config_dir: Path) -> None:
        self._path = config_dir / "rules.json"

    def get_days_to_check_balance(self) -> int:
        data = self._load()
        return int(data.get("daysToCheckBalance", 3))

    def _load(self) -> dict:
        with self._path.open(encoding="utf-8") as handle:
            return json.load(handle)
