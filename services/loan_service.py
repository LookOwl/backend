from dependencies.uow import AppUnitOfWork
from domain.loan import Loan
from domain.user import User
from repositories.loan_repository import LoanRepository

class LoanService:
    def __init__(
            self,
            uow : AppUnitOfWork
        ):
        self.uow = uow

    #Pagination not implemented at repository level
    def get_loans(self, limit:int, offset:int ):
        try:
            list = self.loan_repo.list_all()
            return list
        except Exception:
            raise LoanException
        
class LoanException(Exception): pass