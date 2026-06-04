from pydantic import BaseModel, EmailStr
from core.validators import NonemptyString, PhoneNumberString
from domain.enums.roles_usuario import RolUsuario 


class LoginDto(BaseModel):
    email : EmailStr
    password : NonemptyString
    role: RolUsuario

class RegisterUserDto(BaseModel):
    fullname : NonemptyString
    contact_number : PhoneNumberString
    email : EmailStr
    password : NonemptyString
    role: RolUsuario