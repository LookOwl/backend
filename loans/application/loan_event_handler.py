


from abc import ABC, abstractmethod

from loans.domain.loan import Loan
from loans.domain.loan_events import  LoanEventType, LoanExpired, LoanReturned
from shared.application.event_handler import EventHandler
from shared.domain.event_type import EventType


class LoanEventHandler(EventHandler, ABC):
    
    @abstractmethod
    async def onLoanExpired(self, loan : Loan) -> None:
        pass

    @abstractmethod
    async def onLoanReturned(self, loan:Loan) -> None:
        pass

    async def handle(self, event: EventType) -> None:
        assert isinstance(event,LoanEventType)
        match event:
            case LoanExpired():
                await self.onLoanExpired(event.loan)
            case LoanReturned():
                await self.onLoanReturned(event.loan)
            case _:
                return