from collections.abc import Callable
from datetime import date

from app.application.ports import (
    BalanceNotFoundError,
    BalanceProvider,
    CalendarProvider,
    ProcessingError,
    RulesProvider,
)
from app.domain.models import CaseInput, DomainResult
from app.domain.rules import calculate_working_day, decide_action


class CheckAccountBalanceProcessor:
    def __init__(
        self,
        balance_provider: BalanceProvider,
        calendar_provider: CalendarProvider,
        rules_provider: RulesProvider,
        today_provider: Callable[[], date] = date.today,
    ):
        self._balances = balance_provider
        self._calendar = calendar_provider
        self._rules = rules_provider
        self._today_provider = today_provider

    def process(self, case_input: CaseInput) -> DomainResult:
        account_id = case_input.contracts[0].contractId

        try:
            balance = self._balances.get_balance(account_id)
        except BalanceNotFoundError as exc:
            raise ProcessingError(
                code="ERR_BALANCE_NOT_FOUND",
                message=f"No balance configured for account: {account_id}",
            ) from exc

        return decide_action(
            case_input=case_input,
            balance=balance,
            today=self._today_provider(),
            working_day_calculator=calculate_working_day,
            non_working_days=self._calendar.get_non_working_days(),
            days_to_check=self._rules.get_days_to_check_balance(),
        )
