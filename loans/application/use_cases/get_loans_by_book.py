
from books.domain.book import BookId
from loans.domain.loan_repo import LoanRepository
from shared.application.unit_of_work import UnitOfWork


class GetLoansOfBookUseCase:

    uow : UnitOfWork
    loan_repo : LoanRepository
    
    def __init__(
            self,
            uow : UnitOfWork,
            loan_repo : LoanRepository
        ) -> None:
        self.uow = uow
        self.loan_repo = loan_repo
        

    async def execute( self, book_id : int):
        async with self.uow:
            loans = await self.loan_repo.get_by_book_id(BookId(book_id))
        return loans