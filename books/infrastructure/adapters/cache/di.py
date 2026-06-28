from fastapi import Depends

from books.domain.book_copy_repository import BookCopyRepository
from books.infrastructure.adapters.cache.redis_book_availability_builder import RedisBookAvailabilityBuilder
from books.infrastructure.adapters.cache.redis_book_availability_reader import RedisBookAvailabilityReader
from books.infrastructure.adapters.persistence.di import get_sql_book_repository
from books.infrastructure.di import UnitOfWork
from loans.domain.loan_request_repo import LoanRequestRepository
from loans.infrastructure.adapters.di import get_sql_loan_req_repo
from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController
from shared.infrastructure.persistence.di import get_sql_unit_of_work
from shared.infrastructure.cache.di import get_redis_controller, get_redis_lock_manager
from books.domain.book_availability_builder import BookAvailabilityBuilder
from books.domain.book_availability_reader import BookAvailabilityReader
from books.application.book_availability_facade import BookAvailabilityFacade



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
    book_copy_repository: BookCopyRepository = Depends(get_sql_book_repository), 
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