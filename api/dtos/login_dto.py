from pydantic import BaseModel

class LoginDto(BaseModel):
    email : str
    password : str

class RegisterUserDto(BaseModel):
    fullname : str
    contact_number : int
    email : str
    password : str
