from dataclasses import dataclass

from books.domain.book import BookId


@dataclass
class BookAvailability:
    book_id : BookId
    """Number of books which are not under a soft lock"""
    available_books : int
    """Number of books that are not assigned to a loan"""
    total_books: int