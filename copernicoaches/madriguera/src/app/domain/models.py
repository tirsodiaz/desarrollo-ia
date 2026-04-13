from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ContractItem(BaseModel):
    contractId: str


class AccountClosure(BaseModel):
    dateToCheckBalance: date | None = None
    entity: str


class CaseInput(BaseModel):
    caseId: str
    source: str
    # The original process diagram uses 1-based notation. In Python, the
    # primary account is taken from contracts[0].
    contracts: list[ContractItem] = Field(min_length=1)
    accountClosure: AccountClosure


class BalanceData(BaseModel):
    account_id: str
    amount: float


class Action(StrEnum):
    POSITIVE_BALANCE = "positiveBalance"
    ZERO_BALANCE = "zeroBalance"
    CUSTOMER_NEGATIVE_BALANCE = "customerNegativeBalance"
    BANK_NEGATIVE_BALANCE = "bankNegativeBalance"
    WAIT = "wait"
    CANCEL = "cancel"


class DomainResult(BaseModel):
    case_id: str
    action: Action
    date_time: datetime | None = None


class OutputPayload(BaseModel):
    caseId: str
    action: str
    dateTime: str | None = None


class ErrorEntry(BaseModel):
    code: str
    message: str


class ErrorPayload(BaseModel):
    caseId: str
    taskName: str = "Check Account Balance"
    dateTime: str
    errors: list[ErrorEntry]
