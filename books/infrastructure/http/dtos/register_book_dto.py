from datetime import date
from pydantic import AnyUrl, BaseModel
from shared.infrastructure.http.validators import IsbnString
from shared.infrastructure.http.validators import LanguageString, NonEmptyString, NonEmptyStringList, PositiveInt

class RegisterBookDto(BaseModel):
    title : NonEmptyString
    isbn : IsbnString
    description : NonEmptyString
    editorial : NonEmptyString
    publication_date : date
    cover_url : AnyUrl
    language : LanguageString
    author : NonEmptyStringList
    category : NonEmptyStringList
    page_count : PositiveInt
