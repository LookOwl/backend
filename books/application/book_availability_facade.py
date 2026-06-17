from books.domain.book import BookId
from books.domain.book_availability import BookAvailability
from books.domain.book_availability_builder import BookAvailabilityBuilder
from loans.infrastructure.di import BookAvailabilityReader


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
        while(max_attempts > 0):
            try:
                indices = await self.reader.get_availability(book_id)
                return indices
            except Exception:
                await self.builder.build(book_id)
                max_attempts-=1
                continue
        raise Exception("Impossible to obtain indices")