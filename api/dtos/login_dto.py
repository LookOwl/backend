from pydantic import BaseModel, EmailStr, Field
from core.validators import NonemptyString, PhoneNumberString


class LoginDto(BaseModel):
    email : EmailStr
    password : NonemptyString

class RegisterUserDto(BaseModel):
    fullname : NonemptyString
    contact_number : PhoneNumberString
    email : EmailStr
    password : NonemptyString
