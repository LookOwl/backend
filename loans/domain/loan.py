from dataclasses import dataclass
from books.domain.book import BookId
from books.domain.book_copy import BookCopyId
from loans.domain.loan_status import LoanStatus
from users.domain.user_id import UserId
from datetime import date

@dataclass
class LoanId:
    id: int

@dataclass
class Loan:
    id : LoanId
    user_id : UserId
    book_copy_id : BookCopyId
    book_id : BookId
    approval_date : date
    due_date : date
    return_date : date | None
    status : LoanStatus
    