from dataclasses import dataclass
from enum import Enum
from books.domain.book import BookId

class BookCopyStatus(Enum):
    DISPONIBLE = "DISPONIBLE"
    PRESTADO = "PRESTADO"
    DANADO = "DANADO"

@dataclass
class BookCopyId:
    id : int

@dataclass
class PhysicalBookCopyId:
    physical_id : str

@dataclass
class BookCopy:
    id : BookCopyId
    physical_copy_id: PhysicalBookCopyId
    book_id : BookId
    status: BookCopyStatus

    def reserve(self):
        self.status = BookCopyStatus.PRESTADO

    def release(self) -> None:
        self.status = BookCopyStatus.DISPONIBLE

