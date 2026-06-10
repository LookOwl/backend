from pydantic import BaseModel, EmailStr, field_validator
from core.validators import NonemptyString, PhoneNumberString
from domain.enums.roles_usuario import RolUsuario 


class LoginDto(BaseModel):
    email : EmailStr
    password : NonemptyString
    role: RolUsuario

    @field_validator("role", mode="before")
    @classmethod
    def decode_role(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

class RegisterUserDto(BaseModel):
    fullname : NonemptyString
    contact_number : PhoneNumberString
    email : EmailStr
    password : NonemptyString
    role: RolUsuario

    @field_validator("role", mode="before")
    @classmethod
    def decode_role(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v