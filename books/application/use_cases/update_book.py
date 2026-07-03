from datetime import date
from books.domain.book import Book, BookAuthor, BookCategory, BookCover, BookDescription, BookEditorial, BookISBN, BookId, BookLanguage, BookPageCount, BookPublicationDate, BookTitle
from books.domain.book_repository import BookRepository
from shared.application.unit_of_work import UnitOfWork
from users.domain.user import User
from users.domain.user_id import UserId
from users.domain.user_repository import UserRepository
from users.domain.user_role import UserRole


class UpdateBook:

    def __init__(
        self,
        user_repository : UserRepository,
        book_repository : BookRepository,
        uow : UnitOfWork
    ) -> None:
        self.user_repo = user_repository
        self.book_repository = book_repository
        self.uow = uow

    async def execute(
        self,
        book_id: int,
        user_id: int,
        title : str | None = None,
        isbn : str | None = None,
        description : str | None = None,
        editorial : str | None = None,
        publication_date : date | None = None,
        cover_url : str | None = None,
        language : str | None = None,
        authors : list[str] | None = None,
        categories : list[str] | None = None,
        page_count : int | None = None,
    ):
        async with self.uow:
            user : User | None = await self.user_repo.get_by_id(UserId(uid = user_id))
            if not user:
                raise Exception("User not found")

            if user.role != UserRole.BIBLIOTECARIO:
                raise Exception("Only librarians can update books")

            book : Book | None = await self.book_repository.get_by_id(BookId(id=book_id))
            if not book:
                raise Exception("Book not found")

            if title is not None:
                book.title = BookTitle(title=title)
            if isbn is not None:
                book.isbn = BookISBN(isbn_code=isbn)
            if description is not None:
                book.description = BookDescription(description=description)
            if editorial is not None:
                book.editorial = BookEditorial(editorial=editorial)
            if publication_date is not None:
                book.publication_date = BookPublicationDate(pub_date=publication_date)
            if cover_url is not None:
                book.cover_url = BookCover(url=cover_url)
            if language is not None:
                book.language = BookLanguage(lang=language)
            if authors is not None:
                book.author = BookAuthor(authors=authors)
            if categories is not None:
                book.category = BookCategory(categories=categories)
            if page_count is not None:
                book.page_count = BookPageCount(count=page_count)

            await self.book_repository.update_book(book)
