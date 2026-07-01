from datetime import date
from pydantic import BaseModel
from books.domain.book import Book


class BookDto(BaseModel):

    id: int
    title : str
    isbn : str | None
    description : str
    editorial : str | None
    publication_date : date | None
    cover_url : str | None
    language : str
    author : list[str]
    category : list[str]
    page_count : int | None

    @staticmethod
    def to_dto(book : Book) -> "BookDto":
        return BookDto(
            id=book.book_id.id,
            title=book.title.title,
            isbn=book.isbn.isbn_code if book.isbn else None ,
            description=book.description.description,
            editorial=book.editorial.editorial if book.editorial else None ,
            publication_date=book.publication_date.pub_date if book.publication_date else None,
            cover_url=book.cover_url.url if book.cover_url else None,
            language=book.language.lang,
            author=book.author.authors,
            category=book.category.categories,
            page_count=book.page_count.count if book.page_count else None,
        )
