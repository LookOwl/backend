from pydantic import BaseModel
from domain.enums.estado_prestamos import EstadoPrestamo
from core.validators import NonNegativeInt, PositiveInt

class LoanDto(BaseModel):
    book_id : int
    interest_window : PositiveInt = 168 #Measured in hours: 24 = 1d. Default = 7*24 = 168
    n_days_requested : PositiveInt
