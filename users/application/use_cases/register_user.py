from users.domain.user import User, UserCredentials, UserId, UserRole
from users.domain.user_repository import UserRepository
from users.application.ports import PasswordHasher

class RegisterUser:

    user_repo : UserRepository
    hasher : PasswordHasher

    def __init__(
            self, 
            user_repo : UserRepository,
            password_hasher : PasswordHasher
        ):
        self.user_repo = user_repo
        self.hasher = password_hasher

    async def execute(
        self,
        full_name: str,
        contact_number: str,
        email: str,
        password: str
    ) -> None:
        
        return await self.user_repo.save_user(User(
            id = UserId(-1),
            full_name=full_name,
            contact_number=contact_number,
            role=UserRole.LECTOR,
            credentials=UserCredentials(email,self.hasher.hash_password(password))
        ))