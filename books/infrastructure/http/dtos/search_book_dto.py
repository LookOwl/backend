from datetime import date

from pydantic import BaseModel
from books.domain.book_search_criteria import SortBy
from shared.infrastructure.http.validators import NonNegativeInt


class SearchBookDto(BaseModel):
    query: str = ""
    sort_by: SortBy = SortBy.ID
    ascending: bool = True
    from_date: date = date.min
    to_date: date = date.today()
    limit: NonNegativeInt = 20
    offset: NonNegativeInt = 0


class AdvancedSearchBookDto(BaseModel):
    title: str | None = None
    authors: list[str] = []
    category: list[str] = []
    isbn: str | None = None
    language: str | None = None
    editorial: str | None = None
    sort_by: SortBy = SortBy.ID
    ascending: bool = True
    from_date: date = date.min
    to_date: date = date.today()
    limit: NonNegativeInt = 20
    offset: NonNegativeInt = 0
