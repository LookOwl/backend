from loans.application.loan_request_dispatcher import LoanRequestEventDispatcher
from loans.domain.loan_request_event import LoanRequestCopyAssigned
from shared.application.unit_of_work import UnitOfWork
from loans.domain.loan_request_repo import LoanRequestRepository
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_copy import BookCopyId, BookCopyStatus
from loans.domain.loan_request import LoanRequestId, LoanRequestStatus

class AssignBookCopyToLoanRequestUseCase:

    uow : UnitOfWork
    loan_req_repo : LoanRequestRepository
    book_copy_repo : BookCopyRepository
    loan_request_event_dispatcher : LoanRequestEventDispatcher

    def __init__(
            self,
            uow : UnitOfWork,
            loan_req_repo : LoanRequestRepository,
            book_copy_repo : BookCopyRepository,
            loan_request_event_dispatcher : LoanRequestEventDispatcher
        ) -> None:
        self.uow= uow
        self.loan_req_repo= loan_req_repo
        self.book_copy_repo = book_copy_repo 
        self.loan_request_event_dispatcher = loan_request_event_dispatcher

    async def execute( self, req_id: int, book_copy_id : int ):
        async with self.uow:
            #Check consistency: the loan exists?
            loan_request = await self.loan_req_repo.get_by_id(LoanRequestId(req_id))
            if loan_request is None or loan_request.status != LoanRequestStatus.PENDIENTE: raise InvalidLoanRequestException
            #Check consistency: is the book_copy free?
            book_copy = await self.book_copy_repo.get_by_id(BookCopyId(book_copy_id))
            
            if book_copy is None: raise CopyNoExistsException
            if book_copy.status != BookCopyStatus.DISPONIBLE: raise CopyNoAvailableException
            #else
            book_copy.reserve()
            loan_request.assign_book(BookCopyId(book_copy_id))

            await self.loan_req_repo.update_loan_request(loan_request)
            await self.book_copy_repo.update_book_copy(book_copy)
        
        await self.loan_request_event_dispatcher.notify(
            LoanRequestCopyAssigned(
                loan_request,
                book_copy
            )
        )

class InvalidLoanRequestException(Exception): pass
class CopyNoExistsException(Exception): pass
class CopyNoAvailableException(Exception) : pass