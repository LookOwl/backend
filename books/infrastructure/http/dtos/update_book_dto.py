from pydantic import BaseModel
from datetime import date


class UpdateBookDTO(BaseModel):
    title: str | None = None
    isbn: str | None = None
    description: str | None = None
    editorial: str | None = None
    publication_date: date | None = None
    cover_url: str | None = None
    language: str | None = None
    author: list[str] | None = None
    category: list[str] | None = None
    page_count: int | None = None
