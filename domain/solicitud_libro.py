from dataclasses import dataclass
from typing import Optional
from domain.enums.estado_solicitud import EstadoSolicitud

@dataclass
class BookRequest:
    id: Optional[int]
    user_id: int
    book_id: str
    wait_time: int
    status: EstadoSolicitud
