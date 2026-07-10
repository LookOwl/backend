from books.domain.book import BookId
from books.domain.book_availability import BookAvailability
from books.domain.book_availability_builder import BookAvailabilityBuilder
from books.domain.book_availability_reader import BookAvailabilityCacheMiss, BookAvailabilityReader


class BookAvailabilityFacade:

    reader : BookAvailabilityReader
    builder : BookAvailabilityBuilder

    def __init__(
        self,
        reader : BookAvailabilityReader,
        builder : BookAvailabilityBuilder
    ) -> None:
        self.reader = reader
        self.builder = builder

    async def read_availability(self, book_id : BookId) -> BookAvailability:
        max_attempts = 5
        while max_attempts > 0:
            max_attempts -= 1
            try:
                return await self.reader.get_availability(book_id)
            except BookAvailabilityCacheMiss:
                # Only a genuine cache miss warrants a rebuild. Any other error
                # (lock timeout, Redis down, ...) is re-raised by the reader and
                # propagates instead of masquerading as a miss.
                try:
                    await self.builder.build(book_id)
                except Exception:
                    # A failed rebuild must not escape the retry loop; fall
                    # through and try again until attempts are exhausted.
                    continue
        raise Exception("Impossible to obtain indices")