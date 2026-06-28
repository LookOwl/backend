from pydantic import BaseModel, EmailStr, field_validator
from shared.infrastructure.http.validators import NonEmptyString, PhoneNumberString
from users.domain.user_role import UserRole

class RegisterUserDto(BaseModel):
    fullname : NonEmptyString
    contact_number : PhoneNumberString
    email : EmailStr
    password : NonEmptyString
    role: UserRole

    @field_validator("role", mode="before")
    @classmethod
    def decode_role(cls, v:object):
        if isinstance(v, str):
            return v.upper()
        return v