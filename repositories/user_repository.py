from domain.user import User, UserCredentials
from domain.exceptions import UsuarioNoEncontrado
from db.models.usuario import Usuario, RolUsuario
from sqlalchemy.orm import Session
from sqlalchemy import select

class UserRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_user_lector(self, user: User) -> User:
        orm_user = Usuario(
            nombre = user.full_name,
            email = user.email,
            numero_contacto = user.contact_number,
            hash_contrasena = user.credentials.password_hash
        )
        self.db.add(orm_user)
        self.db.commit()
        self.db.refresh(orm_user)
        return self._to_domain(orm_user)

    def save_user_bibliotecario(self, user: User) -> User:
        orm_user = Usuario(
            nombre = user.full_name,
            email = user.email,
            numero_contacto = user.contact_number,
            hash_contrasena = user.credentials.password_hash,
            rol = RolUsuario.BIBLIOTECARIO
        )
        self.db.add(orm_user)
        self.db.commit()
        self.db.refresh(orm_user)
        return self._to_domain(orm_user)

    def get_user_credentials(self, email : str) -> User:
        query = select(Usuario).where(Usuario.email == email)
        datos = self.db.execute(query).scalar()

        if datos is None:
            raise UsuarioNoEncontrado(email)

        return self._to_domain(datos)

    def get_user_by_id(self, id: int) -> User:
        query = select(Usuario).where(Usuario.id == id)
        datos = self.db.execute(query).scalar()

        if datos is None:
            raise UsuarioNoEncontrado(str(id))

        return self._to_domain(datos)

    def _to_domain(self, usuario: Usuario) -> User:
        credenciales = UserCredentials(
            password_hash = usuario.hash_contrasena
        )
        return User(
            uid = str(usuario.id),
            full_name = usuario.nombre,
            email = usuario.email,
            contact_number= usuario.numero_contacto,
            role = usuario.rol.value,
            credentials = credenciales
        )
