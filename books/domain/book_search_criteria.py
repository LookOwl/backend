from dataclasses import dataclass
from datetime import date
from books.domain.book import BookAuthor, BookCategory, BookLanguage, BookTitle

@dataclass
class BookSearchCriteria:
    title : BookTitle | None = None
    authors : BookAuthor = BookAuthor([])
    category : BookCategory = BookCategory([])
    language : BookLanguage | None = None
    from_date: date | None = None
    to_date: date | None = None

