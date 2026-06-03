from dataclasses import dataclass
from typing import Optional
from domain.enums.estado_solicitud import EstadoSolicitud
from datetime import datetime

@dataclass
class BookRequest:
    id: Optional[int]
    user_id: int
    book_id: int
    copy_code: str
    wait_time: int
    loan_time: int
    status: EstadoSolicitud
    created_at: datetime
    updated_at: datetime
