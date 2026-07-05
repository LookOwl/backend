from shared.application.unit_of_work import UnitOfWork
from users.domain.user import User, UserCredentials, UserId, UserRole
from users.domain.user_repository import UserRepository
from users.application.ports import PasswordHasher

class RegisterUser:

    def __init__(
        self,
        user_repo : UserRepository,
        password_hasher : PasswordHasher,
        uow : UnitOfWork
    ):
        self.user_repo = user_repo
        self.hasher = password_hasher
        self.uow = uow

    async def execute(
        self,
        full_name: str,
        contact_number: str,
        email: str,
        password: str,
        role: UserRole = UserRole.LECTOR
    ) -> None:
        async with self.uow:
            await self.user_repo.save_user(User(
                id = UserId(-1),
                full_name=full_name,
                contact_number=contact_number,
                role=role,
                credentials=UserCredentials(email,self.hasher.hash_password(password))
            ))
        return
