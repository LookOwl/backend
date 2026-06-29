from pydantic import BaseModel
from books.domain.book_copy import BookCopy


class BookCopyDto(BaseModel):

    copy_id: str
    status: str

    @staticmethod
    def to_dto(book_copy: BookCopy) -> "BookCopyDto":
        return BookCopyDto(
            copy_id=book_copy.copy_id.physical_id,
            status=book_copy.status.value
        )
