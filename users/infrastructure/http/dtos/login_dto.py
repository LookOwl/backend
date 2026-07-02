from pydantic import BaseModel, EmailStr
from shared.infrastructure.http.validators import NonEmptyString

class LoginDto(BaseModel):
    email : EmailStr
    password : NonEmptyString
