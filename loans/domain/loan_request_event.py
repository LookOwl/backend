from books.domain.book_copy import BookCopy
from shared.domain.event_type import EventType
from loans.domain.loan_request import LoanRequest
from users.domain.user import User

"""Base class for all loan request events"""
class LoanRequestEvent(EventType):
    pass


# 4 casos
class LoanRequestCreated(LoanRequestEvent):
    loan : LoanRequest
    user : User

    def __init__(self, loan : LoanRequest, user : User) -> None:
        super().__init__()
        self.loan = loan
        self.user = user

    def get_type(self):
        return LoanRequestCreated


class LoanRequestInterestTimeExpired(LoanRequestEvent):
    loan : LoanRequest

    def __init__(self,loan : LoanRequest) -> None:
        super().__init__()
        self.loan = loan

    def get_type(self):
        return LoanRequestInterestTimeExpired


class LoanRequestCopyAssigned(LoanRequestEvent):
    loan : LoanRequest
    book_copy : BookCopy

    def __init__(self,loan : LoanRequest, book_copy : BookCopy) -> None:
        super().__init__()
        self.loan = loan
        self.book_copy = book_copy
    
    def get_type(self):
        return LoanRequestCopyAssigned


class LoanRequestPickupTimeExpired(LoanRequestEvent):
    loan : LoanRequest

    def __init__(self,loan : LoanRequest) -> None:
        super().__init__()
        self.loan = loan
    
    def get_type(self):
        return LoanRequestPickupTimeExpired


