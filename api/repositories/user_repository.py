from api.dtos.login_dto import RegisterUserDto

#Por el momento esto es un mock
class UserRepository:
    
    #mock
    count:int
    users:dict[int,RegisterUserDto]

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
        self.users[self.count] = user
        self.count += 1

    async def getUserByCredentials(
        self,
        email : str
    ):
        for id, u in self.users.items():
            if u.email == email:
                return MockUser(id,u.fullname,u.contact_number,u.email,u.password)
        return None
    
class MockUser:
    id : int
    fullname : str
    contact_number : int
    email : str
    password : str
    role : str 
    def __init__(
        self,
        p0,p1,p2,p3,p4
    ) -> None:
        self.id = p0
        self.fullname = p1
        self.contact_number = p2
        self.email = p3
        self.password = p4
        self.role = "User"
        pass
