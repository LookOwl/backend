from pydantic import BaseModel
from books.domain.book_copy import BookCopyStatus
from shared.infrastructure.http.validators import NonEmptyString


class UpdateBookCopyStatusDTO(BaseModel):
    copy_id: NonEmptyString
    status: BookCopyStatus
