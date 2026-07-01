from datetime import date

from books.domain.book import Book, BookAuthor, BookCategory, BookEditorial, BookISBN, BookLanguage, BookTitle
from books.domain.book_repository import BookRepository
from books.domain.book_search_criteria import AdvancedBookSearchCriteria, BookSearchCriteria, SortBy
from books.domain.result_page import ResultPage
from books.domain.semantic_query import SemanticQuery
from shared.application.unit_of_work import UnitOfWork


class SearchBooks:

    def __init__(
            self,
            book_repository: BookRepository,
            uow: UnitOfWork
    ) -> None:
        self.book_repo = book_repository
        self.uow = uow

    async def execute(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        sort_by: SortBy | None = None,
        ascending: bool = True,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Book]:

        sort_by = sort_by or SortBy.ID

        async with self.uow:
            results: list[Book] = await self.book_repo.search_book(
                BookSearchCriteria(
                    query=SemanticQuery(query=query),
                    sort_by=sort_by,
                    ascending=ascending,
                    from_date=from_date,
                    to_date=to_date,
                ),
                ResultPage(
                    starts_at=offset,
                    number_of_results=limit,
                ),
            )
        return results


class AdvancedSearchBooks:

    def __init__(
            self,
            book_repository: BookRepository,
            uow: UnitOfWork
    ) -> None:
        self.book_repo = book_repository
        self.uow = uow

    async def execute(
        self,
        limit: int = 20,
        offset: int = 0,
        title: str | None = None,
        authors: list[str] | None = None,
        categories: list[str] | None = None,
        isbn: str | None = None,
        language: str | None = None,
        editorial: str | None = None,
        sort_by: SortBy | None = None,
        ascending: bool = True,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[Book]:

        sort_by = sort_by or SortBy.ID

        async with self.uow:
            criteria = AdvancedBookSearchCriteria(
                title=BookTitle(title=title) if title else None,
                authors=BookAuthor(authors or []),
                category=BookCategory(categories or []),
                isbn=BookISBN(isbn_code=isbn) if isbn else None,
                language=BookLanguage(lang=language) if language else None,
                editorial=BookEditorial(editorial=editorial) if editorial else None,
                sort_by=sort_by,
                ascending=ascending,
                from_date=from_date,
                to_date=to_date,
            )
            results: list[Book] = await self.book_repo.advanced_search_book(
                criteria,
                ResultPage(
                    starts_at=offset,
                    number_of_results=limit,
                ),
            )
            return results
