from api.core.security import verify_password, generate_token, hash_password
from api.dtos.login_dto import RegisterUserDto
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
        user = await self.user_repo.getUserCredentials(email)
        print(user)
        if (user is not None) and verify_password(password,user.password) :
            token = generate_token(str(user.uid),user.role)
            return token
        return None

    async def registerUser(self, userDto : RegisterUserDto):
        userDto.password = hash_password(password=userDto.password)
        try:
            await self.user_repo.saveUser(userDto)
            return True
        except Exception as e:
            return False
