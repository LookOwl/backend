from books.domain.book_copy import PhysicalBookCopyId
from loans.application.loan_dispatcher import LoanEventDispatcher
from loans.domain.loan import Loan
from loans.domain.loan_events import LoanReturned
from loans.domain.loan_repo import LoanRepository
from shared.application.unit_of_work import UnitOfWork


class ReturnBookUseCase:
    
    uow : UnitOfWork
    loan_repo : LoanRepository
    loan_event_dispatcher : LoanEventDispatcher

    def __init__(
            self,
            uow : UnitOfWork,
            loan_repo : LoanRepository,
            loan_event_dispatcher : LoanEventDispatcher
        ) -> None:
        self.uow = uow
        self.loan_repo = loan_repo
        self.loan_event_dispatcher = loan_event_dispatcher

    async def execute( self, book_copy : str):
        async with self.uow:
            #First, find the loan
            loan: Loan | None = await self.loan_repo.get_by_physical_book_id(PhysicalBookCopyId(book_copy))
            if loan is None : return LoanNotFoundException
            #Return the loan
            loan.return_book()
            await self.loan_repo.save_loan(loan)
        await self.loan_event_dispatcher.notify(
            LoanReturned(loan)
        )
        return
    
class LoanNotFoundException(Exception): pass