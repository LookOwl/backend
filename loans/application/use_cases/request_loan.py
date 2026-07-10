from datetime import datetime, timezone

from books.application.book_availability_facade import BookAvailabilityFacade
from books.domain.book import Book, BookId
from books.domain.book_repository import BookRepository
from loans.application.loan_request_dispatcher import LoanRequestEventDispatcher
from loans.domain.loan import UserId
from loans.domain.loan_request import LoanRequest, LoanRequestId, LoanRequestStatus, LoanRequestTimeRequested, LoanRequestWaitTime
from loans.domain.loan_request_event import LoanRequestCreated
from loans.domain.loan_request_repo import LoanRequestRepository
from users.domain.user import User
from shared.application.unit_of_work import UnitOfWork
from users.domain.user_repository import UserRepository


class RequestLoan:

    def __init__(
        self,
        uow : UnitOfWork,
        loan_req_repository: LoanRequestRepository,
        book_repository : BookRepository,
        user_repository : UserRepository,
        book_availability_facade : BookAvailabilityFacade,
        loan_event_dispatcher :LoanRequestEventDispatcher
    ) -> None:
        self.book_availability_facade = book_availability_facade
        self.loan_request_repository = loan_req_repository
        self.book_repository = book_repository
        self.user_repository = user_repository
        self.uow = uow
        self.loan_event_dispatcher = loan_event_dispatcher

    async def execute(self, user_id : int, book_id : int,  max_interest_time : int, requested_loan_time : int) -> bool:
        """Exceute the use case. Returns `True` if the request was put on the priviledge queue. `False` if not and is waiting """

        async with self.uow:
            user : User | None = await self.user_repository.get_by_id(id=UserId(uid=user_id))
            book : Book | None = await self.book_repository.get_by_id(book_id=BookId(id=book_id))
            if not user or not book:
                raise Exception("User or Book does not exist")

            #Now, check the availability
            queue_length : int = (await self.book_availability_facade.read_availability(book.book_id)).no_soft_locked_copies

            #No matter what, request is created and put in queue.
            request : LoanRequest = LoanRequest(
                loan_req_id= LoanRequestId(id=0),
                user_id=user.id,
                book_id=book.book_id,
                book_copy_code=None,
                wait_time=LoanRequestWaitTime(time=max_interest_time),
                loan_time=LoanRequestTimeRequested(time=requested_loan_time),
                status=LoanRequestStatus.PENDIENTE,
                created_at=datetime.now(timezone.utc),
                modified_at=datetime.now(timezone.utc)
            )
            #save the request
            await self.loan_request_repository.save_request(request)

        #End of uow clause. If we reach here, a successfully "commit()" happened
        #Notify listeners that a new request was created
        await self.loan_event_dispatcher.notify(LoanRequestCreated(
            request,
            user
        ))

        return True if queue_length > 0 else False
