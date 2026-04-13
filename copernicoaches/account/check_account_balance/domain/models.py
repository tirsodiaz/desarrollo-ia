from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


@dataclass(frozen=True)
class ContractItem:
    contract_id: str


@dataclass(frozen=True)
class AccountClosure:
    date_to_check_balance: date | None = None
    entity: str = ""


@dataclass(frozen=True)
class CaseInput:
    case_id: str
    source: str
    contracts: list[ContractItem] = field(default_factory=list)
    account_closure: AccountClosure = field(default_factory=AccountClosure)

    @classmethod
    def from_dict(cls, payload: dict) -> "CaseInput":
        contracts = [
            ContractItem(contract_id=str(item.get("contractId", "")))
            for item in payload.get("contracts", [])
        ]

        raw_closure = payload.get("accountClosure", {}) or {}
        raw_date = raw_closure.get("dateToCheckBalance")
        parsed_date = date.fromisoformat(raw_date) if raw_date else None

        closure = AccountClosure(
            date_to_check_balance=parsed_date,
            entity=str(raw_closure.get("entity", "")),
        )

        return cls(
            case_id=str(payload.get("caseId", "")),
            source=str(payload.get("source", "")),
            contracts=contracts,
            account_closure=closure,
        )


class Action(str, Enum):
    POSITIVE_BALANCE = "positiveBalance"
    ZERO_BALANCE = "zeroBalance"
    CUSTOMER_NEGATIVE_BALANCE = "customerNegativeBalance"
    BANK_NEGATIVE_BALANCE = "bankNegativeBalance"
    WAIT = "wait"
    CANCEL = "cancel"


@dataclass(frozen=True)
class DomainResult:
    case_id: str
    action: Action
    date_time: datetime | None = None


@dataclass(frozen=True)
class ErrorEntry:
    code: str
    message: str
