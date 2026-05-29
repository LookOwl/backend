from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from infrastructure.database.base import BaseModel
from domain.enums.estado_ejemplares import EstadoEjemplar

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from infrastructure.database.models.libro import Libro
    from infrastructure.database.models.prestamo import Prestamo
    from infrastructure.database.models.solicitud_libro import SolicitudLibro

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
    estado: Mapped[EstadoEjemplar] = mapped_column(default=EstadoEjemplar.DISPONIBLE)

    libro: Mapped[Libro] = relationship(back_populates="ejemplares")
    prestamos: Mapped[list[Prestamo]] = relationship(back_populates="ejemplar")
    solicitudes: Mapped[list[SolicitudLibro]] = relationship(back_populates="ejemplar")
