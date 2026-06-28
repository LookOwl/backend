from pydantic import BaseModel
from shared.infrastructure.http.validators import PositiveInt

class RequestLoanDto(BaseModel):
    book_id : int
    interest_window : PositiveInt = 2 #Measured in days. Default 2, max 13
    n_days_requested : PositiveInt
