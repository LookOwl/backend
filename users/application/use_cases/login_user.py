from shared.application.unit_of_work import UnitOfWork
from users.domain.user_repository import User
from users.domain.user_credential import UserCredentials
from users.domain.user_repository import UserRepository
from users.domain.token import EncryptedToken
from users.application.ports import PasswordHasher, TokenHandler

class LoginUser:

    def __init__(
        self,
        user_repo : UserRepository,
        hasher : PasswordHasher,
        token_handler : TokenHandler,
        uow : UnitOfWork
    ):
        self.user_repo = user_repo
        self.hasher = hasher
        self.token_handler = token_handler
        self.uow = uow


    async def execute(
        self,
        email : str,
        password : str
    ) -> EncryptedToken:
        #Find credentials associated with that email
        async with self.uow:
            credentials : UserCredentials | None = await self.user_repo.find_user_credential(email)
            if not credentials:
                raise Exception("No credentials found")   #TODO(Declare domains errors)
            #If password does not match the hashed one
            if(not self.hasher.verify_password(credentials.stored_password,password)):
                raise Exception("Invalid password") # Temporal
            #If so, find the user
            user : User | None = await self.user_repo.get_by_email(credentials.email)
            if(not user):
                raise Exception("No user found")

        return self.token_handler.generate_token(user_id = user.id, user_role = user.role)
