from pydantic import BaseModel

from shared.infrastructure.http.validators import NonEmptyString

class CreateLoanDto(BaseModel):
    book_physical_copy : NonEmptyString