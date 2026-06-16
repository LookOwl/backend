from books.domain.book_repository import BookRepository
from books.domain.book import Book, BookAuthor, BookTitle
from books.domain.book_search_criteria import BookSearchCriteria

class SearchBook:

    book_repo : BookRepository

    def __init__(
            self,
            book_repository : BookRepository
        ) -> None:
        self.book_repo = book_repository
        

    def execute(self, title: str, authors : list[str]):
        result : list[Book] = self.book_repo.find_similar_books(
            BookSearchCriteria(
                title = BookTitle(title=title),
                authors = BookAuthor(authors=authors)
            )
        )