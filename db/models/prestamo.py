from __future__ import annotations
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from db.base import BaseModel
from domain.enums.estado_prestamos import EstadoPrestamo
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.usuario import Usuario
    from db.models.ejemplar import Ejemplar

class Prestamo(BaseModel):

    """
        Modelo ORM para representación de un préstamo.

        Atributos:
            - codigo_ejemplar: Código asignado para la identificación del ejemplar a prestar.
            - id_usuario_asociado: Identificador de usuario responsable del préstamo.
            - fecha_aprobacion: Fecha de aprobación asignada del préstamo.
            - fecha_vencimiento: Fecha de vencimiento programada del préstamo según la fecha de aprobación.
            - fecha_regreso: Fecha final de regreso del préstamo dado.
            - estado: Estado actual del préstamo.
    """

    __tablename__ = "prestamos"

    codigo_ejemplar: Mapped[str] = mapped_column(ForeignKey("ejemplares.codigo"))
    id_usuario_asociado: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha_aprobacion: Mapped[Optional[date]]
    fecha_vencimiento: Mapped[Optional[date]]
    fecha_regreso: Mapped[Optional[date]]
    estado: Mapped[EstadoPrestamo] = mapped_column(default=EstadoPrestamo.PENDIENTE)

    usuario: Mapped[Usuario] = relationship(back_populates="prestamos")
    ejemplar: Mapped[Ejemplar] = relationship(back_populates="prestamos")
