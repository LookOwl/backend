from books.domain.book_copy import BookCopy
from loans.application.loan_request_event_handler import LoanRequestEventHandler
from loans.domain.loan_request import LoanRequest
from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController
from users.domain.user import User


class RedisLoanRequestEventHandler(LoanRequestEventHandler):

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

    async def onCreateLoanRequest(self, user : User, loan : LoanRequest):
        #If a loan is created, then there is one more book with a soft lock
        #Notice the index can be negative (which is very convenient for us)
        async with self.redis_lock_manager.acquire(str(loan.book_id.id)):
            await self.redis_controller.dec_available_slots(loan.book_id.id)
        return
    
    async def onExpiredInterestTime(self, loan : LoanRequest):
        #A loan request expired on the queue. No book was assigned to it
        async with self.redis_lock_manager.acquire(str(loan.book_id.id)):
            await self.redis_controller.inc_available_slots(loan.book_id.id)
        return

    
    async def onCopyAssigned(self, book_copy : BookCopy, loan : LoanRequest):
        #A hard lock over a book was done.
        #Decrement both indices
        async with self.redis_lock_manager.acquire(str(loan.book_id.id)):
            await self.redis_controller.dec_available_slots(loan.book_id.id)
            await self.redis_controller.dec_total_copies(loan.book_id.id)
        return

    
    async def onPickupTimeExpired(self, loan : LoanRequest):
        #A loan request expired with a book assigned to it. 
        # Increment both indices
        async with self.redis_lock_manager.acquire(str(loan.book_id.id)):
            await self.redis_controller.inc_available_slots(loan.book_id.id)
            await self.redis_controller.inc_total_copies(loan.book_id.id)
        return