from dataclasses import dataclass

from books.domain.book import BookId


@dataclass
class BookAvailability:
    book_id : BookId
    """Number of books which are not under a soft lock"""
    no_soft_locked_copies : int
    """Number of books that are not assigned to a loan"""
    no_hard_locked_copies: int