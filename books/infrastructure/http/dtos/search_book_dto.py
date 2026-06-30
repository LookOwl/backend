from datetime import date

from pydantic import BaseModel
from books.domain.book_search_criteria import SortBy
from shared.infrastructure.http.validators import NonEmptyString, NonNegativeInt


class SearchBookDto(BaseModel):
    query: NonEmptyString
    sort_by: SortBy | None = None
    ascending: bool = True
    from_date: date | None = None
    to_date: date | None = None
    limit: NonNegativeInt = 20
    offset: NonNegativeInt = 0


class AdvancedSearchBookDto(BaseModel):
    title: str | None = None
    authors: list[str] = []
    category: list[str] = []
    isbn: str | None = None
    language: str | None = None
    editorial: str | None = None
    sort_by: SortBy | None = None
    ascending: bool = True
    from_date: date | None = None
    to_date: date | None = None
    limit: NonNegativeInt = 20
    offset: NonNegativeInt = 0
