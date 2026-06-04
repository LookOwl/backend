from domain.user import User, UserCredentials
from domain.exceptions import UsuarioNoEncontrado
from infrastructure.database.models.usuario import Usuario
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_user(self, user: User) -> User:
        orm_user = Usuario(
            nombre = user.full_name,
            email = user.email,
            numero_contacto = user.contact_number,
            hash_contrasena = user.credentials.password_hash,
            rol = user.role
        )
        self.db.add(orm_user)
        await self.db.flush()
        await self.db.refresh(orm_user)
        return self._to_domain(orm_user)

    async def get_user_credentials(self, email : str) -> User:
        query = select(Usuario).where(Usuario.email == email)
        result = await self.db.execute(query)
        datos = result.scalar()

        if datos is None:
            raise UsuarioNoEncontrado(email)

        return self._to_domain(datos)

    async def get_user_by_id(self, id: int) -> User:
        query = select(Usuario).where(Usuario.id == id)
        result = await self.db.execute(query)
        datos = result.scalar()

        if datos is None:
            raise UsuarioNoEncontrado(str(id))

        return self._to_domain(datos)

    def _to_domain(self, usuario: Usuario) -> User:
        credenciales = UserCredentials(
            password_hash = usuario.hash_contrasena
        )
        return User(
            uid = usuario.id,
            full_name = usuario.nombre,
            email = usuario.email,
            contact_number= usuario.numero_contacto,
            role = usuario.rol,
            credentials = credenciales
        )
