from __future__ import annotations

from typing import Protocol


class BalanceProvider(Protocol):
    def get_balance(self, account_id: str) -> float: ...


class BalanceNotFoundError(Exception):
    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        super().__init__(f"Balance no encontrado para cuenta: {account_id}")
