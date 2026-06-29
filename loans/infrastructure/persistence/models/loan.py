from __future__ import annotations
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from shared.infrastructure.persistence.models.base import BaseModel
from loans.domain.loan_status import LoanStatus
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from users.infrastructure.persistence.models.user import Usuario
    from books.infrastructure.persistence.models.book_copy import Ejemplar
    from loans.infrastructure.persistence.models.loan_request import SolicitudLibro


class Prestamo(BaseModel):

    """
        Modelo ORM para representación de un préstamo.

        Atributos:
            - codigo_ejemplar: Código asignado para la identificación del ejemplar a prestar.
            - id_usuario_asociado: Identificador de usuario responsable del préstamo.
            - fecha_aprobacion: Fecha de aprobación asignada del préstamo.
            - fecha_vencimiento: Fecha de vencimiento programada del préstamo según la fecha de aprobación.
            - fecha_regreso: Fecha final de regreso del préstamo dado.
            - dias_prestamo: Duración del préstamo en días (máximo 13).
            - estado: Estado actual del préstamo.
    """

    __tablename__ = "prestamos"

    codigo_ejemplar: Mapped[str] = mapped_column(ForeignKey("ejemplares.codigo"))
    id_usuario_asociado: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha_aprobacion: Mapped[date]
    fecha_vencimiento: Mapped[date]
    fecha_regreso: Mapped[Optional[date]]
    estado: Mapped[LoanStatus] = mapped_column(default=LoanStatus.ACTIVO)

    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes_libro.id"), unique=True)

    usuario: Mapped[Usuario] = relationship(back_populates="prestamos", lazy='joined')
    ejemplar: Mapped[Ejemplar] = relationship(back_populates="prestamos", lazy='joined')
    solicitud: Mapped[SolicitudLibro] = relationship(back_populates="prestamo", lazy='joined')
