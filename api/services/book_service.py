from domain.book import Book
from api.dtos.book_dto import RegisterBookDto
from repositories.book_repository import BookRepository

class BookService:
    def __init__(self, book_repo : BookRepository) -> None:
        self.repo = book_repo


    async def registerBook(self, book : RegisterBookDto) -> int:
        toCreate = Book(
            uid=0,
            title=book.title,
            isbn=book.isbn,
            description=book.isbn,
            editorial=book.editorial,
            publication_date=book.publication_date,
            cover_url=book.cover_url,
            language=book.language,
            author=book.author,
            category=book.category,
            page_count=book.page_count,
            n_copies=0
        )
        saved = self.repo.save_book(toCreate)
        return saved.uid 

    