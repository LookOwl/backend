from datetime import date
from pydantic import BaseModel
from loans.domain.loan_status import LoanStatus


class LoanDto(BaseModel):
    id : int
    user_id : int
    book_copy_id : int
    book_id : int
    approval_date : date
    due_date : date
    return_date : date | None
    status : LoanStatus