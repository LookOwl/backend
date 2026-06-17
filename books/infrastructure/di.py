from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from books.application.book_availability_facade import BookAvailabilityFacade
from books.application.use_cases.register_book import RegisterBook
from books.application.use_cases.search_books import SearchBook
from books.domain.book_availability_builder import BookAvailabilityBuilder
from books.domain.book_availability_reader import BookAvailabilityReader
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_repository import BookRepository
from books.infrastructure.adapters.redis_book_availability_builder import RedisBookAvailabilityBuilder
from books.infrastructure.adapters.redis_book_availability_reader import RedisBookAvailabilityReader
from books.infrastructure.adapters.sql_book_repository import SQLBookRepository
from loans.domain.loan_request_repo import LoanRequestRepository
from loans.infrastructure.di import get_sql_loan_req_repo
from old.dependencies.repositories import get_book_copy_repository
from shared.application.unit_of_work import UnitOfWork
from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController
from shared.infrastructure.di import get_async_sql_session, get_redis_controller, get_redis_lock_manager, get_sql_unit_of_work
from users.domain.user_repository import UserRepository
from users.infrastructure.di import get_sql_user_repo

def get_redis_book_availability_reader(
        redis_lock_manager : RedisLockManager = Depends(get_redis_lock_manager),
        redis_controller : RedisController = Depends(get_redis_controller)
):
    return RedisBookAvailabilityReader(
        redis_lock_manager,
        redis_controller
    )

def get_redis_book_availability_builder(
    loan_req_repository: LoanRequestRepository = Depends(get_sql_loan_req_repo), 
    book_copy_repository: BookCopyRepository = Depends(get_book_copy_repository), 
    uow: UnitOfWork = Depends(get_sql_unit_of_work), 
    redis_controller: RedisController = Depends(get_redis_controller), 
    redis_lock_manager: RedisLockManager = Depends(get_redis_lock_manager) 
):
    return RedisBookAvailabilityBuilder(
        loan_req_repository,
        book_copy_repository,
        uow,
        redis_controller,
        redis_lock_manager
    )

def get_redis_book_availability_facade(
        reader : BookAvailabilityReader = Depends(get_redis_book_availability_reader),
        builder : BookAvailabilityBuilder = Depends(get_redis_book_availability_builder)
):
    return BookAvailabilityFacade(
        reader,
        builder
    )

def get_sql_book_repository( 
    session : AsyncSession = Depends(get_async_sql_session) 
):
    return SQLBookRepository(
        session
    )

def get_search_book_uc(
    book_repo : BookRepository = Depends(get_sql_book_repository),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
):
    return SearchBook(
        book_repo,
        uow
    )

def get_register_book_uc(
    book_repository : BookRepository = Depends(get_sql_book_repository),
    user_repository : UserRepository = Depends(get_sql_user_repo),
    uow : UnitOfWork = Depends(get_sql_unit_of_work)
):
    return RegisterBook(
        book_repository,
        user_repository,
        uow
    )
