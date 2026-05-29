from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from db.base import BaseModel
from domain.enums.estado_solicitud import EstadoSolicitud
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.usuario import Usuario
    from db.models.libro import Libro

class SolicitudLibro(BaseModel):

    """
        Modelo ORM para representar una solicitud de libro.

        Atributos:
            - id_usuario: Identificador del usuario que realiza la solicitud.
            - libro_id: Identificador del libro que se desea prestar.
            - tiempo_espera: Tiempo de espera asignado en días.
            - estado: Estado de la solicitud, 'pendiente' como predeterminado.
    """

    __tablename__ = "solicitudes_libro"

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    id_libro: Mapped[str] = mapped_column(ForeignKey("libros.id"))
    tiempo_espera: Mapped[int]
    estado: Mapped[EstadoSolicitud] = mapped_column(default=EstadoSolicitud.PENDIENTE)

    usuario: Mapped[Usuario] = relationship(back_populates="solicitudes")
    libro: Mapped[Libro] = relationship(back_populates="solicitudes")
