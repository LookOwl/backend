from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, ForeignKey
from shared.infrastructure.persistence.models.base import BaseModel
from loans.domain.loan_request_status import LoanRequestStatus
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from users.infrastructure.persistence.models.user import Usuario
    from books.infrastructure.persistence.models.book import Libro
    from books.infrastructure.persistence.models.book_copy import Ejemplar
    from loans.infrastructure.persistence.models.loan import Prestamo


class SolicitudLibro(BaseModel):

    """
        Modelo ORM para representar una solicitud de libro.

        Atributos:
            - id_usuario: Identificador del usuario que realiza la solicitud.
            - libro_id: Identificador del libro que se desea prestar.
            - tiempo_espera: Tiempo de espera asignado en días.
            - tiempo_prestamo: Tiempo del préstamo solicitado en días.
            - estado: Estado de la solicitud, 'pendiente' como predeterminado.
    """

    __tablename__ = "solicitudes_libro"

    __table_args__ = (
        CheckConstraint("tiempo_prestamo < 15", name="ck_tiempo_prestamo"),
        CheckConstraint("tiempo_espera < 8", name="ck_tiempo_espera")
    )

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    id_libro: Mapped[int] = mapped_column(ForeignKey("libros.id"))
    codigo_ejemplar: Mapped[Optional[str]] = mapped_column(ForeignKey("ejemplares.codigo"))
    tiempo_espera: Mapped[int]
    tiempo_prestamo: Mapped[int]
    estado: Mapped[LoanRequestStatus] = mapped_column(default=LoanRequestStatus.PENDIENTE)

    usuario: Mapped[Usuario] = relationship(back_populates="solicitudes")
    libro: Mapped[Libro] = relationship(back_populates="solicitudes")
    ejemplar: Mapped[Ejemplar] = relationship(back_populates="solicitudes")
    prestamo: Mapped[Optional[Prestamo]] = relationship(back_populates="solicitud", uselist=False, lazy='joined')
