from sqlalchemy.orm import Session
from domain.book_copy import BookCopy
from db.models.ejemplar import Ejemplar
from sqlalchemy import select

class BookCopyRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_copies(self, libro_id: str) -> list[BookCopy]:
        query = select(Ejemplar).where(Ejemplar.libro_id == int(libro_id))
        copies = list(self.db.execute(query).scalars().all())
        return [self._to_domain(copy) for copy in copies]

    def save_copies(self, libro_id: str, book_copy: BookCopy) -> BookCopy:
        ejemplar = Ejemplar(
            libro_id = int(libro_id),
            codigo = book_copy.codigo,
            estado = book_copy.estado
        )
        self.db.add(ejemplar)
        self.db.commit()
        self.db.refresh(ejemplar)
        return self._to_domain(ejemplar)

    def _to_domain(self, ejemplar: Ejemplar) -> BookCopy:
        return BookCopy(
            codigo=ejemplar.codigo,
            estado=ejemplar.estado.value
        )
