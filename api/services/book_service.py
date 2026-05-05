from domain.book import Book
from api.dtos.book_dto import RegisterBookDto, SearchBookDto
from repositories.book_repository import BookRepository

class BookService:
    def __init__(self, book_repo : BookRepository) -> None:
        self.repo = book_repo

    async def getBooks(self,params : SearchBookDto) -> list[Book] :
        data = []
        
        if params.limit is not None and params.offset is not None:
            data = self.repo.get_books(
                title=params.title,
                author=params.author,
                limit=params.limit+1,
                offset=params.offset
            )
        elif params.limit is not None:
            data = self.repo.get_books(
                title=params.title,
                author=params.author,
                limit=params.limit+1
            )
        else:
            data = self.repo.get_books(
                title=params.title,
                author=params.author
            )
        
        return data

    async def registerBook(self, book : RegisterBookDto) -> int:
        toCreate = Book(
            id=0,
            title=book.title,
            isbn=book.isbn,
            description=book.isbn,
            editorial=book.editorial,
            publication_date=book.publication_date,
            cover_url=book.cover_url,
            language=book.language,
            author=book.author,
            category=book.category,
            page_count=book.page_count
        )
        saved = self.repo.save_book(toCreate)
        return saved.uid
