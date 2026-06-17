
from books.domain.book import BookId
from books.domain.book_availability import BookAvailability
from books.domain.book_availability_store import BookAvailabilityStore
from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController


class RedisBookAvailabilityStore(BookAvailabilityStore):
    """prefixes:
    $bookId:avSlots => available slots
    $bookId:totCopies => total copies
    $bookId:valid => if the cache entry is valid
    """

    redis_lock_manager : RedisLockManager
    redis_controller : RedisController

    def __init__(
            self,
            redis_lock_manager : RedisLockManager,
            redis_controller : RedisController
        ) -> None:
        super().__init__()
        self.redis_lock_manager = redis_lock_manager
        self.redis_controller = redis_controller

    async def get_availability(self, book_id: BookId) -> BookAvailability:
        async with self.redis_lock_manager.acquire(str(book_id.id)):
            available_books = await self.redis_controller.get_available_slots(book_id.id)
            total_copies = await self.redis_controller.get_total_copies(book_id.id)
        return BookAvailability(
            book_id,
            available_books,
            total_copies
        )

    