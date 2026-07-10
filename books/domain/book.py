from dataclasses import dataclass
from datetime import date

from users.domain.user import User, UserRole

@dataclass
class BookId:
    id : int

@dataclass
class BookTitle:
    title : str

@dataclass
class BookISBN:
    isbn_code : str

@dataclass
class BookDescription:
    description : str

@dataclass
class BookEditorial:
    editorial : str

@dataclass
class BookPublicationDate:
    pub_date : date

@dataclass
class BookCover:
    url : str

@dataclass
class BookLanguage:
    lang : str

@dataclass
class BookAuthor:
    authors : list[str]

@dataclass
class BookCategory:
    categories : list[str]

@dataclass
class BookPageCount:
    count : int

@dataclass
class Book:
    book_id : BookId
    title : BookTitle
    isbn : BookISBN | None
    description : BookDescription
    editorial : BookEditorial | None
    publication_date : BookPublicationDate | None
    cover_url : BookCover | None
    language : BookLanguage
    author : BookAuthor
    category : BookCategory
    page_count : BookPageCount | None



class BookBuilder:
    
    book_id : BookId
    title : BookTitle
    isbn : BookISBN | None
    description : BookDescription
    editorial : BookEditorial | None
    publication_date : BookPublicationDate | None
    cover_url : BookCover | None
    language : BookLanguage
    author : BookAuthor
    category : BookCategory
    page_count : BookPageCount | None

    def __init__(self) -> None:
        self.book_id = BookId(0)
        self.title = BookTitle("")
        self.isbn = None
        self.description = BookDescription("")
        self.editorial = None
        self.publication_date = None
        self.cover_url = None
        self.language = BookLanguage("")
        self.author = BookAuthor([])
        self.category = BookCategory([])
        self.page_count = None

    def with_id ( self, book_id : BookId ):
        self.book_id = book_id
        return self

    def with_title( self, title : BookTitle ):
        self.title = title
        return self
    
    def with_isbn ( self, isbn : BookISBN ):
        self.isbn = isbn
        return self

    def with_description( self, description : BookDescription ):
        self.description = description
        return self

    def with_editorial(self, editorial: BookEditorial):
        self.editorial = editorial
        return self

    def with_publication_date(self, publication_date: BookPublicationDate ):
        self.publication_date = publication_date
        return self

    def with_cover_url(self, cover_url: BookCover ):
        self.cover_url = cover_url
        return self


    def with_language(self, language: BookLanguage ):  
        self.language = language
        return self

    def with_author(self, author: BookAuthor ):
        self.author = author
        return self

    def with_category(self, category: BookCategory ): 
        self.category = category
        return self

    def with_page_count(self, page_count: BookPageCount ): 
        self.page_count = page_count
        return self

    def create(self,user : User):
        if(user.role != UserRole.BIBLIOTECARIO):
            raise Exception("Only librarians can create books")
        else:
            return Book(
                book_id=self.book_id,
                title=self.title,
                isbn=self.isbn,
                description=self.description,
                editorial=self.editorial,
                publication_date=self.publication_date,
                cover_url=self.cover_url,
                language=self.language,
                author=self.author,
                category=self.category,
                page_count=self.page_count
            )