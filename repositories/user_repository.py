from api.dtos.login_dto import RegisterUserDto
from domain.user import User, UserCredentials
#Por el momento esto es un mock
class UserRepository:
    
    #mock
    count:int
    users:dict[str,RegisterUserDto]

    def __init__(
        self,
        db
    ) -> None:
        self.db = db
        self.count = 0
        self.users = {}

    async def saveUser(
        self,
        user : RegisterUserDto
    ):
        for id, u in self.users.items():
            if u.email == user.email:
                raise Exception(f"Correo ya registrado por usuario con id: {id}")
        self.users[str(self.count)] = user
        self.count += 1

    async def getUserCredentials(
        self,
        email : str
    ) -> UserCredentials | None:
        for id, u in self.users.items():
            if u.email == email:
                return UserCredentials(
                    str(id),
                    u.email,
                    u.password,
                    "not implemented"
                )
        return None
    
    async def findUserById(
        self,
        user_id : str
    ) -> User | None:
        print(f"inside user repo, repo : {self.users}, argument id : {user_id}")
        for id, u in self.users.items():
            if id == user_id:
                return User(
                    user_id,
                    u.fullname,
                    u.contact_number,
                    "roles not implemented yet"
                )
        return None
