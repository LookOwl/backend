from pydantic import BaseModel
from datetime import date

class RegisterBookDto(BaseModel):
    title : str
    isbn : str
    description : str
    editorial : str
    publication_date : date
    cover_url : str
    language : str
    author : list[str]
    category : list[str]
    page_count : int

class SearchBookDto(BaseModel):
    title : str | None
    author : str | None
    limit : int | None
    offset : int | None