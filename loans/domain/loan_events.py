

from loans.domain.loan import Loan
from shared.domain.event_type import EventType

"""Base class for all loan events"""
class LoanEventType(EventType):
    pass

#Two events:
#When a loan expires
#When a loan is returned

class LoanExpired(LoanEventType):
    loan : Loan

    def __init__(
            self,
            loan : Loan
        ) -> None:
        super().__init__()
        self.loan = loan

    def get_type(self) -> type:
        return LoanExpired
    
class LoanReturned(LoanEventType):
    loan : Loan

    def __init__(
            self,
            loan : Loan
        ) -> None:
        super().__init__()
        self.loan = loan
    def get_type(self) -> type:
        return LoanReturned