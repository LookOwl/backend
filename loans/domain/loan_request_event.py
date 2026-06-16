from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from loans.domain.loan_request import LoanRequestId

class LoanRequestEventType(Enum):
    """A new request arrived to the queue"""
    CREATED = "CREATED"
    """Means the request expired due to its wait time"""
    EXPIRED = "EXPIRED"
    """Means the max time for pickup was due"""
    PICKUP_EXPIRED = "PICKUP_EXPIRED"
    """A book copy was assigned to the loan request"""
    ASSIGNED = "ASSIGNED"

@dataclass
class LoanRequestEvent:
    loan_id : LoanRequestId
    event_type : LoanRequestEventType


class LoanRequestEventHandler(ABC):    
    @abstractmethod
    async def handle(self,event:LoanRequestEvent)-> None:
        pass

class LoanRequestBus(ABC):

    @abstractmethod
    async def suscribe(self, suscriber: LoanRequestEventHandler):
        pass

    @abstractmethod
    async def publish(self, event: LoanRequestEventType) -> None:
        pass