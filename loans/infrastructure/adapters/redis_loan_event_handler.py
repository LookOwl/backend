

from loans.application.loan_event_handler import LoanEventHandler
from loans.domain.loan import Loan
from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController


class RedisLoanEventHandler(LoanEventHandler):

    redis_controller : RedisController
    redis_lock_manager : RedisLockManager

    def __init__(
            self,
            redis_controller : RedisController,
            redis_lock_manager : RedisLockManager
        ) -> None:
        super().__init__()
        self.redis_controller = redis_controller
        self.redis_lock_manager = redis_lock_manager


    async def onLoanExpired(self, loan: Loan) -> None:
        #Literally do nothing, because if it expires, nothing changes respect
        # of the indices
        return
    
    async def onLoanReturned(self, loan: Loan) -> None:
        book_id = loan.book_id.id
        str_book_id= str(loan.book_id)
        #If a book is returned, means there is one more book without a lock
        async with self.redis_lock_manager.acquire(str_book_id):
            await self.redis_controller.inc_total_copies(book_id)
            await self.redis_controller.inc_available_slots(book_id)
        return