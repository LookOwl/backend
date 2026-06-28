from dataclasses import dataclass, field
from datetime import date
from books.domain.book import BookAuthor, BookCategory, BookLanguage, BookTitle

@dataclass
class BookSearchCriteria:
    title : BookTitle | None = None
    authors : BookAuthor = field(default_factory=lambda: BookAuthor([]))
    category : BookCategory = field(default_factory=lambda: BookCategory([]))
    language : BookLanguage | None = None
    from_date: date | None = None
    to_date: date | None = None

