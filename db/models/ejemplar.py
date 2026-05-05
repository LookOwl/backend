from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String
from db.base import BaseModel
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from db.models.libro import Libro

class EstadoEjemplar(Enum):
    DISPONIBLE = "disponible"
    PRESTADO = "prestado"
    DANADO = "dañado"

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

    libros: Mapped["Libro"] = relationship(back_populates="ejemplar")
