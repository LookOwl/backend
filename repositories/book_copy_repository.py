from typing import Optional
from sqlalchemy.orm import Session
from domain.book_copy import BookCopy
from domain.enums.estado_ejemplares import EstadoEjemplar
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

    def get_status(self, codigo: str) -> Optional[EstadoEjemplar]:
        stmt = select(Ejemplar).where(Ejemplar.codigo == codigo)
        ejemplar = self.db.execute(stmt).scalars().first()
        if ejemplar is None:
            return None
        return self._to_domain(ejemplar).estado

    def mark_available(self, codigo: str) -> Optional[BookCopy]:
        return self._set_status(codigo, EstadoEjemplar.DISPONIBLE)

    def mark_lent(self, codigo: str) -> Optional[BookCopy]:
        return self._set_status(codigo, EstadoEjemplar.PRESTADO)

    def mark_damaged(self, codigo: str) -> Optional[BookCopy]:
        return self._set_status(codigo, EstadoEjemplar.DANADO)

    def _set_status(self, codigo: str, status: EstadoEjemplar) -> Optional[BookCopy]:
        stmt = select(Ejemplar).where(Ejemplar.codigo == codigo)
        ejemplar = self.db.execute(stmt).scalars().first()
        if ejemplar is None:
            return None

        ejemplar.estado = status
        self.db.commit()
        self.db.refresh(ejemplar)
        return self._to_domain(ejemplar)

    def _to_domain(self, ejemplar: Ejemplar) -> BookCopy:
        return BookCopy(
            codigo=ejemplar.codigo,
            estado=ejemplar.estado
        )
