from dataclasses import dataclass
from typing import Optional
from domain.enums.estado_solicitud import EstadoSolicitud

@dataclass
class BookRequest:
    id: Optional[int]
    user_id: int
    copy_code: str
    wait_time: int
    status: EstadoSolicitud
