from pydantic import BaseModel, NonNegativeInt

class CreateLoanDto(BaseModel):
    req_id : NonNegativeInt