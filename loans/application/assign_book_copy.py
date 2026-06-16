

from books.domain.book import Book, BookId
from books.domain.book_availability_store import BookAvailabilityStore
from books.domain.book_copy import BookCopyId, BookCopyStatus
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_copy import BookCopy
from books.domain.book_repository import BookRepository
from loans.domain.loan_request import LoanRequest, LoanRequestId
from loans.domain.loan_request_repo import LoanRequestRepository
from shared.application.unit_of_work import UnitOfWork


class AssignBookCopyToLoanRequest:

    uow : UnitOfWork
    book_availability_store : BookAvailabilityStore
    book_repo : BookRepository
    loan_request_repo : LoanRequestRepository

    def __init__(
            self,
            uow : UnitOfWork,
            book_availability_store : BookAvailabilityStore,
            book_copy_repository : BookCopyRepository,
            book_repository : BookRepository,
            loan_request_repository : LoanRequestRepository
        ) -> None:
        self.uow = uow
        self.book_availability_store = book_availability_store
        self.book_copy_repo = book_copy_repository
        self.book_repo = book_repository
        self.loan_request_repo = loan_request_repository

    async def execute(self, book_copy : str, book_id : int, request_id : int):
        async with self.uow:
            #Find if the book_copy, the book and the request still exists
            copy : BookCopy | None = await self.book_copy_repo.get_by_id(BookCopyId(physical_id=book_copy))
            book : Book | None = await self.book_repo.get_by_id(BookId(id=book_id))
            request : LoanRequest | None = await self.loan_request_repo.get_by_id(id=LoanRequestId(id=request_id))
            if(not copy or not book or not request): raise Exception("Book, book_copy or request does not exist")
            
            copy.reserve()
            request.assign
            #If so, then update the status of the loan, the status of the copy, and apply a hard lock
            await self.book_copy_repo.update_book_copy(copy)
            