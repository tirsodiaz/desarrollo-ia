from __future__ import annotations

from datetime import date

from check_account_balance.domain.decision_engine import decide_action
from check_account_balance.domain.models import CaseInput, DomainResult
from check_account_balance.ports.balance_provider import BalanceNotFoundError, BalanceProvider
from check_account_balance.ports.calendar_provider import CalendarProvider
from check_account_balance.ports.config_provider import ConfigProvider, ProcessingError


class CheckAccountBalanceProcessor:
    def __init__(
        self,
        balance_provider: BalanceProvider,
        calendar_provider: CalendarProvider,
        config_provider: ConfigProvider,
    ) -> None:
        self._balance_provider = balance_provider
        self._calendar_provider = calendar_provider
        self._config_provider = config_provider

    def process(self, case_input: CaseInput) -> DomainResult:
        account_id = self._extract_account_id(case_input)

        try:
            balance = self._balance_provider.get_balance(account_id)
        except BalanceNotFoundError as exc:
            raise ProcessingError("ERR001", f"Balance no encontrado para cuenta: {account_id}") from exc

        non_working_days = self._calendar_provider.get_non_working_days()
        days_to_check = self._config_provider.get_days_to_check_balance()

        return decide_action(
            case_input=case_input,
            balance=balance,
            today=date.today(),
            non_working_days=non_working_days,
            days_to_check=days_to_check,
        )

    def _extract_account_id(self, case_input: CaseInput) -> str:
        if not case_input.contracts:
            raise ProcessingError("ERR002", f"Caso {case_input.case_id} sin contratos asociados")

        contract_id = case_input.contracts[0].contract_id.strip()
        if not contract_id:
            raise ProcessingError("ERR003", f"Caso {case_input.case_id} con contractId vacío")

        return contract_id
