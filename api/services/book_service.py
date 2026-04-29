from models.book import Book
from api.dtos.book_dto import RegisterBookDto


class BookService:
    def __init__(self, book_repo) -> None:
        self.repo = book_repo
        

    def registerBook(self, book : RegisterBookDto):
        toCreate = Book(
            uid="",
            title=book.title,
            author=book.author,
            category=book.category,
            isbn=book.isbn,
            n_copies=0
        )
        ##Aquí va una llamada al repo