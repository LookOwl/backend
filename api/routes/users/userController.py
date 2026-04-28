from fastapi import APIRouter
from api.dtos.loginDto import LoginDto , RegisterUserDto

router = APIRouter(prefix="/users",tags=["users"])

@router.post("/login")
def login(loginDto:LoginDto):
    return f"Recibido : {loginDto.email} , {loginDto.password}"

@router.post("/register")
def register(registerDto : RegisterUserDto):
    return f"registrado {registerDto.username}, {registerDto.email}, {registerDto.password}"

