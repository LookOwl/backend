
from pydantic import BaseModel, NonNegativeInt
from shared.infrastructure.http.validators import NonEmptyString


class AssignBookDto(BaseModel):
    req_id : NonNegativeInt
    book_copy_code : NonEmptyString
