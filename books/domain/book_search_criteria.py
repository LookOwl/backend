from dataclasses import dataclass
from books.domain.book import BookAuthor, BookTitle

@dataclass
class BookSearchCriteria:
    title : BookTitle
    authors : BookAuthor


