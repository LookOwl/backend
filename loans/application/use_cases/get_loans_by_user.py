
from loans.domain.loan import Loan
from loans.domain.loan_repo import LoanRepository
from shared.application.unit_of_work import UnitOfWork
from users.domain.user_id import UserId


class GetLoansOfUserUseCase:
    
    uow : UnitOfWork
    loan_repo : LoanRepository
    
    def __init__(
            self,
            uow : UnitOfWork,
            loan_repo : LoanRepository
        ) -> None:
        self.uow = uow
        self.loan_repo = loan_repo
    

    async def execute(self, user_id : int) -> list[Loan]:
        async with self.uow:
            #Quite simple: just pull the loans
            loans = await self.loan_repo.get_by_user(UserId(user_id))
        return loans
