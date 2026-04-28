from pydantic import BaseModel

class LoginDto(BaseModel):
    email : str
    password : str

class RegisterUserDto(BaseModel):
    username : str
    email : str
    password : str
