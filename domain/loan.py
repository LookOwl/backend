from dataclasses import dataclass
from datetime import date
from domain.enums.estado_prestamos import EstadoPrestamo
from typing import Optional

@dataclass
class Loan:
    id: Optional[int]
    user_id: int
    copy_code: str
    aproval_date: Optional[date]
    due_date: Optional[date]
    retrival_date: Optional[date]
    status: EstadoPrestamo
