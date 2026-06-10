from core.security import verify_password, generate_token, hash_password, decode_token
from api.dtos.login_dto import RegisterUserDto
from domain.user import User, UserCredentials
from domain.enums.roles_usuario import RolUsuario
from uow.ApplicationUOW import AppUnitOfWork
from domain.exceptions import UsuarioNoEncontrado

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
        return user

    async def registerUser(self, userDto : RegisterUserDto):
        userDto.password = hash_password(password=userDto.password)
        try:
            async with self.uow as uow : 
                # Comprobar que el usuario no exista ya
                try:
                    await uow.user_repo.get_user_credentials(userDto.email)
                except UsuarioNoEncontrado:
                    # El usuario no existe, proceder a guardarlo
                    created_user = await uow.user_repo.save_user(User(
                        uid=0,
                        full_name=userDto.fullname,
                        email=userDto.email,
                        contact_number=userDto.contact_number,
                        role=userDto.role,
                        credentials=UserCredentials(
                            password_hash=userDto.password
                        )
                    ))
                    return created_user
                # Si no se lanzó UsuarioNoEncontrado, el email ya está registrado
                raise UserAlreadyExistsException()
        except UserAlreadyExistsException:
            # No envolver esta excepción — el controlador la maneja como 409
            raise
        except Exception as e:
            raise UnknownException(e)

class UserAlreadyExistsException(Exception): pass
class UserNotFoundException(Exception): pass
class UnknownException(Exception): pass