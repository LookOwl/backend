from fastapi import Depends, Request

from books.application.book_availability_facade import BookAvailabilityFacade
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_repository import BookRepository
from loans.application.use_cases.assign_copy_to_request import AssignBookCopyToLoanRequestUseCase
from loans.application.use_cases.register_new_loan import CreateLoanUseCase
from loans.domain.loan_repo import LoanRepository
from loans.domain.loan_request_repo import LoanRequestRepository

from loans.application.use_cases.get_priviledged_requests import GetPriviledgedRequests
from loans.application.use_cases.request_loan import RequestLoan
from loans.infrastructure.adapters.di import get_sql_loan_repo, get_sql_loan_req_repo
from shared.application.unit_of_work import UnitOfWork
from shared.infrastructure.persistence.di import get_sql_unit_of_work
from books.infrastructure.adapters.cache.di import get_redis_book_availability_facade
from books.infrastructure.adapters.persistence.di import get_sql_book_copy_repository, get_sql_book_repository
from users.domain.user_repository import UserRepository
from loans.application.loan_request_dispatcher import LoanRequestEventDispatcher
from users.infrastructure.di import get_sql_user_repo

def get_loan_request_dispatcher(
    request : Request
):
    assert isinstance(request.app.state.loan_request_dispatcher, LoanRequestEventDispatcher)
    return request.app.state.loan_request_dispatcher


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

def get_assign_book_copy_uc(
        uow : UnitOfWork = Depends(get_sql_unit_of_work),
        loan_req_repo : LoanRequestRepository = Depends(get_sql_loan_req_repo),
        book_copy_repo : BookCopyRepository = Depends(get_sql_book_copy_repository),
        loan_event_dispatcher : LoanRequestEventDispatcher = Depends(get_loan_request_dispatcher)
):
    return AssignBookCopyToLoanRequestUseCase(
        uow,
        loan_req_repo,
        book_copy_repo,
        loan_event_dispatcher
    )


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

def get_start_loan_uc(
    uow : UnitOfWork = Depends(get_sql_unit_of_work),
    loan_req_repo : LoanRequestRepository = Depends(get_sql_loan_req_repo),
    loan_repo : LoanRepository = Depends(get_sql_loan_repo)
):
    return CreateLoanUseCase(
        uow,
        loan_req_repo,
        loan_repo
    )