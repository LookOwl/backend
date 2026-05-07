from pydantic import BaseModel, AnyUrl
from datetime import date
from core.validators import NonemptyString, NonEmptyStringList, PositiveInt, LanguageString, IsbnString

class RegisterBookDto(BaseModel):
    title : NonemptyString
    isbn : IsbnString
    description : NonemptyString
    editorial : NonemptyString
    publication_date : date
    cover_url : AnyUrl
    language : LanguageString
    author : NonEmptyStringList
    category : NonEmptyStringList
    page_count : PositiveInt

class SearchBookDto(BaseModel):
    title : NonemptyString | None
    author : NonemptyString | None
    limit : PositiveInt | None
    offset : PositiveInt | None