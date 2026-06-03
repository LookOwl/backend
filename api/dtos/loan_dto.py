from pydantic import BaseModel
from domain.enums.estado_prestamos import EstadoPrestamo
from core.validators import NonNegativeInt, PositiveInt

class LoanDto(BaseModel):
    book_id : int
    interest_window : PositiveInt = 2 #Measured in days. Default 2, max 13
    n_days_requested : PositiveInt
