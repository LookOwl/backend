from core.security import verify_password, generate_token, hash_password, decode_token
from api.dtos.login_dto import RegisterUserDto
from domain.user import User, UserCredentials
from domain.enums.roles_usuario import RolUsuario
from repositories.user_repository import UserRepository

class AuthService:
    def __init__(
            self,
            user_repo : UserRepository
        ) -> None:
        self.user_repo = user_repo

    async def validateUser(
            self,
            email : str,
            password : str
        ) -> str | None:
        user = self.user_repo.get_user_credentials(email)
        print(user)
        if (user is not None) and verify_password(password,user.credentials.password_hash):
            # Pequeña corrección al cambiar el tipo de user.role, al convertirlo a str
            token = generate_token(user_id=user.uid,user_role=str(user.role))
            return token
        return None

    async def validateToken(self,token: str):
        payload = decode_token(token)
        user = self.user_repo.get_user_by_id(int(payload['sub']))
        return user

    async def registerUser(self, userDto : RegisterUserDto):
        userDto.password = hash_password(password=userDto.password)
        try:
            self.user_repo.save_user(User(
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
