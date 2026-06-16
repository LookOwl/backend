from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from shared.infrastructure.persistence.models.base import BaseModel
from books.domain.book_copy import BookCopyStatus

from books.infrastructure.persistence.models.book import Libro
from loans.infrastructure.persistence.models.loan import Prestamo
from loans.infrastructure.persistence.models.loan_request import SolicitudLibro

class Ejemplar(BaseModel):

    """
        Modelo ORM para representar ejemplares de un libro
        Atributos:
            - libro_id: ID del libro al que pertenece el ejemplar
            - código: Código único del ejemplar físico
            - estado: Estado actual del ejemplar
    """

    __tablename__ = "ejemplares"

    libro_id: Mapped[int] = mapped_column(ForeignKey("libros.id"))
    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    estado: Mapped[BookCopyStatus] = mapped_column(default=BookCopyStatus.DISPONIBLE)

    libro: Mapped[Libro] = relationship(back_populates="ejemplares",lazy='joined')
    prestamos: Mapped[list[Prestamo]] = relationship(back_populates="ejemplar",lazy='selectin')
    solicitudes: Mapped[list[SolicitudLibro]] = relationship(back_populates="ejemplar",lazy='selectin')
