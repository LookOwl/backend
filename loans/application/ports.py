from abc import ABC, abstractmethod
from shared.application.event_handler import EventHandler
from loans.domain.loan_request_event import LoanRequestEvent,LoanRequestCreated, LoanRequestInterestTimeExpired, LoanRequestCopyAssigned, LoanRequestPickupTimeExpired
from books.domain.book_copy import BookCopy
from shared.domain.event_type import EventType
from loans.domain.loan_request import LoanRequest
from users.domain.user import User

class LoanRequestEventHandler(EventHandler,ABC):
    
    @abstractmethod
    async def onCreateLoanRequest(self, user : User, loan : LoanRequest):
        pass
    
    @abstractmethod
    async def onExpiredInterestTime(self, loan : LoanRequest):
        pass

    @abstractmethod
    async def onCopyAssigned(self, book_copy : BookCopy, loan : LoanRequest):
        pass

    @abstractmethod
    async def onPickupTimeExpired(self, loan : LoanRequest):
        pass

    async def handle(self, event : EventType ) -> None:
        if (not issubclass(event.get_type(),LoanRequestEvent)):
            return
        else:
            match(event):
                case LoanRequestCreated():
                    await self.onCreateLoanRequest(event.user,event.loan)
                case LoanRequestInterestTimeExpired():
                    await self.onExpiredInterestTime(event.loan)
                case LoanRequestCopyAssigned():
                    await self.onCopyAssigned(event.book_copy,event.loan)
                case LoanRequestPickupTimeExpired():
                    await self.onPickupTimeExpired(event.loan)
                case _:
                    return
    