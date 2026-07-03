from datetime import datetime

from loans.domain.loan import Loan, LoanId
from loans.domain.loan_repo import LoanRepository
from loans.domain.loan_request import LoanRequestId
from loans.domain.loan_request_repo import LoanRequestRepository
from loans.domain.loan_request_status import LoanRequestStatus
from loans.domain.loan_status import LoanStatus
from shared.application.unit_of_work import UnitOfWork


class CreateLoanUseCase:

    uow : UnitOfWork
    loan_req_repo : LoanRequestRepository
    loan_repo : LoanRepository

    def __init__(
            self,
            uow : UnitOfWork,
            loan_req_repo : LoanRequestRepository,
            loan_repo : LoanRepository
    ) -> None:
        self.uow = uow
        self.loan_req_repo = loan_req_repo
        self.loan_repo = loan_repo

    async def execute( self, loan_req_id : int ):
        async with self.uow:
            loan_req = await self.loan_req_repo.get_by_id(LoanRequestId(loan_req_id))
            if loan_req is None: raise LoanRequestNotFoundException
            #loan request found. Check its status. It should be in NOTIFICADA state
            if loan_req.book_copy_code is None or loan_req.status != LoanRequestStatus.NOTIFICADA: raise LoanRequestInconsistentStatus
            # Status checked. Now proceed to create the Loan object
            new_loan = Loan(
                LoanId(0),   #Repository save methods always ignore this
                loan_req.user_id,
                loan_req.book_copy_code,
                loan_req.book_id,
                datetime.now(),
                datetime.now() + loan_req.loan_time.to_timedelta(),
                None,
                LoanStatus.ACTIVO
            )
            await self.loan_repo.save_loan(new_loan)
        return
                
class LoanRequestNotFoundException(Exception) : pass
class LoanRequestInconsistentStatus(Exception) : pass