from users.domain.user_repository import User
from users.domain.user_credential import UserCredentials
from users.domain.user_repository import UserRepository
from users.domain.token import Token
from application.ports import PasswordHasher, TokenHandler
class LoginUser:

    user_repo : UserRepository
    hasher : PasswordHasher
    token_handler : TokenHandler

    def __init__(
            self,
            user_repo : UserRepository,
            hasher : PasswordHasher,
            token_handler : TokenHandler
        ):
        self.user_repo = user_repo
        self.hasher = hasher
        self.token_handler = token_handler
        pass

    def execute(
            self,
            email : str,
            password : str
        ) -> Token:
        #Find credentials associated with that email
        credentials : UserCredentials = self.user_repo.find_user_credential(email)
        if(credentials is None) : raise Exception   #TODO(Declare domains errors)
        #If password does not match the hashed one
        if(not self.hasher.verify_password(credentials.stored_password,password)):
            raise Exception # Temporal
        #If so, find the user
        user : User = self.user_repo.get_by_email(credentials.email)
        return self.token_handler.generate_token(user_id = user.id, user_role = user.role)