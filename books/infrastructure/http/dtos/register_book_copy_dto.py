from pydantic import BaseModel
from books.domain.book_copy import BookCopyStatus
from shared.infrastructure.http.validators import NonEmptyString


class RegisterBookCopyDto(BaseModel):
    copy_id : NonEmptyString
    status : BookCopyStatus
