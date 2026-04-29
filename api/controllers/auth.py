from fastapi import APIRouter, Depends, HTTPException
from api.dtos.login_dto import LoginDto , RegisterUserDto
from api.services.auth_service import AuthService
from api.services.exports.di import *

router = APIRouter(prefix="/users",tags=["users"])

@router.post("/login")
async def login(
    loginDto:LoginDto, 
    authService : AuthService = Depends(get_auth_service), 
):
    token = await authService.validateUser(loginDto.email,loginDto.password)
    if token is None:
        raise HTTPException(
            status_code=401,
            detail = "User not found"
        )
    return {
        "access_token" : token,
        "token_type" : "bearer"
    }

@router.post("/register")
async def register(registerDto : RegisterUserDto, authService : AuthService = Depends(get_auth_service)):
    success = await authService.registerUser(registerDto)
    if(not success):
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )
    return f"registrado {registerDto.fullname}, {registerDto.email}, {registerDto.password}"

