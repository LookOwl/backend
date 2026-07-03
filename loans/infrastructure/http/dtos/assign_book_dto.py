
from pydantic import BaseModel, NonNegativeInt


class AssignBookDto(BaseModel):
    req_id : NonNegativeInt
    book_copy_id : NonNegativeInt
