from datetime import date
from books.domain.book import BookAuthor, BookBuilder, BookCategory, BookCover, BookDescription, BookEditorial, BookISBN, BookLanguage, BookPageCount, BookPublicationDate, BookTitle
from books.domain.book_repository import BookRepository
from books.domain.book import Book
from shared.application.unit_of_work import UnitOfWork
from users.domain.user import User
from users.domain.user_id import UserId
from users.domain.user_repository import UserRepository


class RegisterBook:

    book_repo : BookRepository
    user_repo : UserRepository
    uow : UnitOfWork

    def __init__(
            self,
            book_repository : BookRepository,
            user_repository : UserRepository,
            uow : UnitOfWork
        ) -> None:
        self.book_repo = book_repository
        self.user_repo = user_repository
        self.uow = uow

    async def execute(
            self,
            title : str,
            isbn : str,
            description : str,
            editorial : str,
            publication_date : date,
            cover_url : str,
            language : str,
            author : list[str],
            category : list[str],
            page_count : int,
            user_id : int
        ):
            async with self.uow:
                user : User | None = await self.user_repo.get_by_id(UserId(uid = user_id))
                if( not user ):
                    raise Exception("User not found")
                
                book : Book = (
                    BookBuilder()
                    .with_title(BookTitle(title=title))
                    .with_isbn(BookISBN(isbn_code=isbn))
                    .with_description(BookDescription(description=description))
                    .with_editorial(BookEditorial(editorial = editorial))
                    .with_publication_date(BookPublicationDate(pub_date= publication_date))
                    .with_cover_url(BookCover(url = cover_url))
                    .with_language(BookLanguage(lang = language))
                    .with_author(BookAuthor(authors=author))
                    .with_category(BookCategory(categories=category))
                    .with_page_count(BookPageCount(count=page_count))
                    .create(user)
                )

                await self.book_repo.save_book(book)

            return
