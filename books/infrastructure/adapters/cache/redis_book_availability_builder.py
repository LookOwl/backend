from books.domain.book import BookId
from books.domain.book_availability_builder import BookAvailabilityBuilder
from shared.application.unit_of_work import UnitOfWork
from loans.domain.loan_request_repo import LoanRequestRepository
from books.domain.book_copy_repository import BookCopyRepository
from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController


class RedisBookAvailabilityBuilder(BookAvailabilityBuilder):

    loan_req_repository : LoanRequestRepository
    redis_controller : RedisController
    book_copy_repository : BookCopyRepository
    uow : UnitOfWork
    redis_lock_manager : RedisLockManager

    def __init__(
            self,
            loan_req_repository : LoanRequestRepository,
            book_copy_repository : BookCopyRepository,
            uow : UnitOfWork,
            redis : RedisController,
            redis_lock_manager : RedisLockManager
        ) -> None:
        super().__init__()
        self.loan_req_repository = loan_req_repository
        self.redis_controller = redis
        self.book_copy_repository = book_copy_repository
        self.uow = uow
        self.redis_lock_manager = redis_lock_manager

    async def build(self, book_id: BookId) -> None:
        async with self.uow:
            queue_length = await self.loan_req_repository.count_pending_by_book_id(book_id)
            no_hard_locked_copies = await self.book_copy_repository.count_available_copies_per_book(book_id)

        #Then
        no_soft_locked_copies = no_hard_locked_copies - queue_length
        async with self.redis_lock_manager.acquire(str(book_id.id)):
            await self.redis_controller.set_indices(
                book_id.id,
                no_hard_locked_copies,
                no_soft_locked_copies
            )


