from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from books.domain.book import BookAuthor, BookCategory, BookEditorial, BookISBN, BookLanguage, BookTitle
from books.domain.semantic_query import SemanticQuery


class SortBy(StrEnum):
    TITLE = "title"
    DATE = "date"
    ID = "id"


@dataclass
class BookSearchCriteria:
    query: SemanticQuery
    sort_by: SortBy
    ascending: bool
    from_date: date | None = None
    to_date: date | None = None


@dataclass
class AdvancedBookSearchCriteria:
    title: BookTitle | None = None
    authors: BookAuthor = field(default_factory=lambda: BookAuthor([]))
    category: BookCategory = field(default_factory=lambda: BookCategory([]))
    isbn: BookISBN | None = None
    language: BookLanguage | None = None
    editorial: BookEditorial | None = None
    sort_by: SortBy = SortBy.ID
    ascending: bool = True
    from_date: date | None = None
    to_date: date | None = None
