from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from books.application.book_availability_facade import BookAvailabilityFacade
from books.domain.book_repository import BookRepository
from loans.domain.loan_request_repo import LoanRequestRepository
from loans.infrastructure.adapters.sql_loan_req_repository import SQLLoanRequestRepository
from loans.infrastructure.http.http_controller import GetPriviledgedRequests, RequestLoan
from shared.application.unit_of_work import UnitOfWork
from shared.infrastructure.di import get_sql_unit_of_work
from books.infrastructure.di import get_redis_book_availability_facade, get_sql_book_repository
from users.domain.user_repository import UserRepository
from loans.application.loan_request_dispatcher import LoanRequestEventDispatcher
from users.infrastructure.di import get_sql_user_repo
from loans.infrastructure.adapters.sql_loan_repository import SQLLoanRepository
from shared.infrastructure.di import get_async_sql_session

def get_sql_loan_repo(
    async_session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLLoanRepository(
        async_session
    )

def get_sql_loan_req_repo(
        async_session : AsyncSession = Depends(get_async_sql_session)
):
    return SQLLoanRequestRepository(
        async_session
    )

def get_priviledged_requests_uc(
        uow: UnitOfWork = Depends(get_sql_unit_of_work), 
        book_repo: BookRepository = Depends(get_sql_book_repository),
        loan_request_repo: LoanRequestRepository = Depends(get_sql_loan_req_repo),
        book_availability_facade: BookAvailabilityFacade = Depends(get_redis_book_availability_facade)
):
    return GetPriviledgedRequests(
        uow,
        book_repo,
        loan_request_repo,
        book_availability_facade
    )

def get_loan_request_dispatcher(
    request : Request
):
    assert isinstance(request.app.state.loan_request_dispatcher, LoanRequestEventDispatcher)
    return request.app.loan_request_dispatcher

def get_request_loan_uc(
    uow: UnitOfWork = Depends(get_sql_unit_of_work),
    loan_req_repository: LoanRequestRepository = Depends(get_sql_loan_req_repo),
    book_repository: BookRepository = Depends(get_sql_book_repository),
    user_repository: UserRepository = Depends(get_sql_user_repo),
    book_availability_facade: BookAvailabilityFacade = Depends(get_redis_book_availability_facade),
    loan_event_dispatcher: LoanRequestEventDispatcher = Depends(get_loan_request_dispatcher)
):
    return RequestLoan(
        uow,
        loan_req_repository,
        book_repository,
        user_repository,
        book_availability_facade,
        loan_event_dispatcher
    )