from books.domain.book_repository import BookRepository
from books.domain.book import Book, BookAuthor, BookTitle
from books.domain.book_search_criteria import BookSearchCriteria
from books.domain.result_page import ResultPage
from shared.application.unit_of_work import UnitOfWork

class SearchBook:

    book_repo : BookRepository
    uow : UnitOfWork


    def __init__(
            self,
            book_repository : BookRepository,
            uow : UnitOfWork
        ) -> None:
        self.book_repo = book_repository
        self.uow = uow
        

    async def execute(self, title: str | None, authors : list[str], limit: int, offset: int):
        async with self.uow :
            result : list[Book] = await self.book_repo.find_by_criteria(
                BookSearchCriteria(
                    title = BookTitle(title=title) if title else None,
                    authors = BookAuthor(authors=authors)
                ),
                ResultPage(
                    starts_at=offset,
                    number_of_results=limit
                )
            )
        return result