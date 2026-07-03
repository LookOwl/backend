from pydantic import BaseModel
from books.domain.book_copy import BookCopyStatus


class UpdateBookCopyStatusDTO(BaseModel):
    status: BookCopyStatus = BookCopyStatus.DISPONIBLE
