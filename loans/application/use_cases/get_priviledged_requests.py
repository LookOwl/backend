from books.domain.book import Book, BookId
from books.domain.book_availability_store import BookAvailabilityStore
from books.domain.book_repository import BookRepository
from loans.domain.loan_request import LoanRequest
from loans.domain.loan_request_repo import LoanRequestRepository
from shared.application.unit_of_work import UnitOfWork


class GetPriviledgedRequests:

    loan_request_repo : LoanRequestRepository
    book_repository : BookRepository
    book_availability_service : BookAvailabilityStore
    uow : UnitOfWork

    def __init__(
            self,
            uow : UnitOfWork,
            book_repo : BookRepository,
            loan_request_repo : LoanRequestRepository,
            book_availability_service : BookAvailabilityStore
        ) -> None:
        self.loan_request_repo = loan_request_repo
        self.book_repository = book_repo
        self.book_availability_service = book_availability_service
        self.uow = uow

    async def execute(self, book_id : int):
        async with self.uow:
            book : Book | None = await self.book_repository.get_by_id(BookId(id=book_id))
            if not book: raise Exception("No book found")
            
            n_priviledged_requests : int = (await self.book_availability_service.get_availability(book.book_id)).total_books
            
            requests : list[LoanRequest] = await self.loan_request_repo.get_n_first_pending_by_book_id(
                book.book_id,
                n_priviledged_requests
            )

        return requests