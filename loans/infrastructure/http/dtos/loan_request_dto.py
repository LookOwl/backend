

from pydantic import BaseModel

from loans.domain.loan_request import LoanRequest, LoanRequestStatus


class LoanRequestDto(BaseModel):
    loan_id : int
    user_id : int
    book_id : int
    book_copy_code : str | None
    loan_time : int
    status : LoanRequestStatus

    @staticmethod
    def to_dto(loan_req : LoanRequest) -> "LoanRequestDto":
        return LoanRequestDto(
            loan_id = loan_req.loan_req_id.id,
            user_id = loan_req.user_id.uid,
            book_id=loan_req.book_id.id,
            book_copy_code=loan_req.book_copy_code.physical_id if loan_req.book_copy_code else None,
            loan_time=loan_req.loan_time.time,
            status= loan_req.status
        )