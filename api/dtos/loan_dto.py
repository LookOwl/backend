from pydantic import BaseModel
from domain.enums.estado_prestamos import EstadoPrestamo
from core.validators import NonNegativeInt, PositiveInt

class LoanDto(BaseModel):
    book_copy_id : str
    n_days_requested : PositiveInt

class UpdateLoanDto(BaseModel):
    loan_id : NonNegativeInt
    status : EstadoPrestamo
