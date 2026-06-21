from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, ForeignKey
from infrastructure.database.base import BaseModel
from domain.enums.estado_solicitud import EstadoSolicitud
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from infrastructure.database.models.usuario import Usuario
    from infrastructure.database.models.libro import Libro
    from infrastructure.database.models.ejemplar import Ejemplar
    from infrastructure.database.models.prestamo import Prestamo

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
    codigo_ejemplar: Mapped[str] = mapped_column(ForeignKey("ejemplares.codigo"))
    tiempo_espera: Mapped[int]
    tiempo_prestamo: Mapped[int]
    estado: Mapped[EstadoSolicitud] = mapped_column(default=EstadoSolicitud.PENDIENTE)

    usuario: Mapped[Usuario] = relationship(back_populates="solicitudes")
    libro: Mapped[Libro] = relationship(back_populates="solicitudes")
    ejemplar: Mapped[Ejemplar] = relationship(back_populates="solicitudes")
    prestamo: Mapped[Optional[Prestamo]] = relationship("Prestamo", back_populates="solicitud", uselist=False, lazy='joined')


# Late import to satisfy SQLAlchemy mapper resolution
from infrastructure.database.models.prestamo import Prestamo  # noqa: E402
