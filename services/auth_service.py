from core.security import verify_password, generate_token, hash_password, decode_token
from api.dtos.login_dto import RegisterUserDto
from domain.user import User, UserCredentials
from domain.enums.roles_usuario import RolUsuario
from uow.ApplicationUOW import AppUnitOfWork

class AuthService:
    
    uow : AppUnitOfWork

    def __init__(
            self,
            uow : AppUnitOfWork
        ) -> None:
        self.uow = uow

    async def validateUser(
            self,
            email : str,
            password : str
        ) -> str | None:
        
        async with self.uow as uow:
            user = await uow.user_repo.get_user_credentials(email)
        
        if (user is not None) and verify_password(password,user.credentials.password_hash):
            # Pequeña corrección al cambiar el tipo de user.role, al convertirlo a str
            token = generate_token(user_id=user.uid,user_role=str(user.role))
            return token
        
        return None

    async def validateToken(self,token: str):
        payload = decode_token(token)
        
        async with self.uow as uow:
            user = await uow.user_repo.get_user_by_id(int(payload['sub']))
            print(user)
        return user

    async def registerUser(self, userDto : RegisterUserDto):
        userDto.password = hash_password(password=userDto.password)
        try:
            async with self.uow as uow : 
                await uow.user_repo.save_user(User(
                    uid="",
                    full_name=userDto.fullname,
                    email=userDto.email,
                    contact_number=userDto.contact_number,
                    role=RolUsuario.LECTOR,
                    credentials=UserCredentials(
                        password_hash=userDto.password
                    )
                ))
            return True
        except Exception as e:
            print(e)
            return False
