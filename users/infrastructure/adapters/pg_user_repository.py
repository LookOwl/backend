from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from users.domain.user import User
from users.domain.user_credential import HashedPassword, UserCredentials
from users.domain.user_id import UserId
from users.domain.user_repository import UserRepository
from users.infrastructure.persistence.models.user import Usuario


class SQLUserRepository(UserRepository):

    async_session : AsyncSession

    def __init__(
            self,
            async_session : AsyncSession
        ) -> None:
        super().__init__()
        self.async_session = async_session


    async def get_by_id(self,id : UserId) -> User | None:
        user = (await self.async_session.execute(
            select(Usuario).where(Usuario.id == id.uid)
        )).scalar_one_or_none()
        
        if not user: return None

        return User(
            UserId(user.id),
            full_name=user.nombre,
            contact_number=user.numero_contacto,
            role=user.rol,
            credentials=UserCredentials(
                user.email,
                HashedPassword(user.hash_contrasena)
            )
        )
    
    async def get_by_email(self, email : str )-> User | None:
        user = (await self.async_session.execute(
            select(Usuario).where(Usuario.email == email)
        )).scalar_one_or_none()
        
        if not user: return None

        return User(
            UserId(user.id),
            full_name=user.nombre,
            contact_number=user.numero_contacto,
            role=user.rol,
            credentials=UserCredentials(
                user.email,
                HashedPassword(user.hash_contrasena)
            )
        )
    
    
    async def find_user_credential(self, email : str ) -> UserCredentials | None:
        user = (await self.async_session.execute(
            select(Usuario).where(Usuario.email == email)
        )).scalar_one_or_none()
        
        if not user: return None

        return UserCredentials(
            user.email,
            HashedPassword(user.hash_contrasena)
        )
    
    async def save_user( self, new_user : User) -> None:
        self.async_session.add(
            Usuario(
                nombre = new_user.full_name,
                email = new_user.credentials.email,
                numero_contacto = new_user.contact_number,
                hash_contrasena = new_user.credentials.stored_password,
                rol = new_user.role
            )
        )
        await self.async_session.flush()
        return

    
    async def delete_user( self, id : UserId ) -> None:
        await self.async_session.execute(
            delete(Usuario)
            .where(Usuario.id == id.uid)
        )
        await self.async_session.flush()
        return
    
    async def update_user( self, user : User ) -> None:
        await self.async_session.execute(
            update(Usuario)
            .where(Usuario.id == user.id.uid)
            .values(
                nombre=user.full_name,
                email = user.credentials.email,
                numero_contacto = user.contact_number,
                rol = user.role,
                hash_contrasena = user.credentials.stored_password
            )
        )
        await self.async_session.flush()
        return