from dataclasses import dataclass
from datetime import  datetime, timedelta

from books.domain.book import BookId
from books.domain.book_copy import BookCopyId
from users.domain.user_id import UserId
from loans.domain.loan_request_status import LoanRequestStatus

@dataclass
class LoanRequestId:
    id : int

@dataclass
class LoanRequestWaitTime:
    time : int
    
    def to_timedelta(self) -> timedelta:
        return timedelta(hours=self.time)

@dataclass
class LoanRequestTimeRequested:
    time : int

    def to_timedelta(self)-> timedelta:
        return timedelta(days=self.time)

@dataclass
class LoanRequest:

    loan_id : LoanRequestId
    user_id: UserId
    book_id: BookId
    book_copy_code : BookCopyId | None
    wait_time: LoanRequestWaitTime  
    loan_time: LoanRequestTimeRequested
    status: LoanRequestStatus
    created_at : datetime
    modified_at : datetime

    def expire(self):
        if(datetime.now() - self.created_at >= self.wait_time.to_timedelta()):
            self.status = LoanRequestStatus.CANCELADA
        else:
            raise Exception("Not possible to expire")

    def assign_book(self, copy_id : BookCopyId):
        self.book_copy_code = copy_id
        self.status = LoanRequestStatus.ASIGNADA 