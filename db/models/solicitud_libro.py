from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from db.base import BaseModel
from domain.enums.estado_solicitud import EstadoSolicitud
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.usuario import Usuario
    from db.models.ejemplar import Ejemplar

class SolicitudLibro(BaseModel):

    """
        Modelo ORM para representar una solicitud de libro.

        Atributos:
            - id_usuario: Identificador del usuario que realiza la solicitud.
            - codigo_ejemplar: Código del ejemplar solicitado.
            - tiempo_espera: Tiempo de espera asignado en días.
    """

    __tablename__ = "solicitudes_libro"

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    codigo_ejemplar: Mapped[str] = mapped_column(ForeignKey("ejemplares.codigo"))
    tiempo_espera: Mapped[int]
    estado: Mapped[EstadoSolicitud] = mapped_column(default=EstadoSolicitud.PENDIENTE)

    usuario: Mapped[Usuario] = relationship(back_populates="solicitudes")
    ejemplar: Mapped[Ejemplar] = relationship(back_populates="solicitudes")
