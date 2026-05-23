from domain.loan import Loan
from domain.user import User
from api.dtos.loan_dto import UpdateLoanDto
from repositories.loan_repository import LoanRepository

class LoanService:
    def __init__(
            self,
            loan_repo: LoanRepository
        ):
        self.loan_repo = loan_repo

    #Pagination not implemented at repository level
    def get_loans(self, limit:int, offset:int ):
        try:
            list = self.loan_repo.list_all()
            return list
        except Exception:
            raise LoanException

    def updateLoanStatus(self, loan_dto : UpdateLoanDto, u : User):
        try:
            loan = self.loan_repo.get_by_id(loan_dto.loan_id)
            loan.status = loan.status
            new_loan = self.loan_repo.update(loan_id=loan_dto.loan_id,loan_entity=loan)
            return new_loan
        except Exception:
            raise LoanException


class LoanException(Exception): pass