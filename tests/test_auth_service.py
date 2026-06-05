import jwt
import pytest

from api.dtos.login_dto import RegisterUserDto
from core.security import ALGORITHM, SECRET_KEY, generate_token, hash_password, verify_password
from domain.enums.roles_usuario import RolUsuario
from domain.exceptions import UsuarioNoEncontrado
from domain.user import User, UserCredentials
from services.auth_service import AuthService, UnknownException


class FakeUserRepository:
    def __init__(self) -> None:
        self._users_by_email: dict[str, User] = {}
        self._users_by_id: dict[int, User] = {}
        self._next_id = 1

    async def save_user(self, user: User) -> User:
        if user.email in self._users_by_email:
            raise ValueError("user already exists")

        stored_user = User(
            uid=self._next_id,
            full_name=user.full_name,
            email=user.email,
            contact_number=user.contact_number,
            role=user.role,
            credentials=UserCredentials(password_hash=user.credentials.password_hash),
        )
        self._next_id += 1
        self._users_by_email[stored_user.email] = stored_user
        self._users_by_id[stored_user.uid] = stored_user
        return stored_user

    async def get_user_credentials(self, email: str) -> User:
        user = self._users_by_email.get(email)
        if user is None:
            raise UsuarioNoEncontrado(email)
        return user

    async def get_user_by_id(self, id: int) -> User:
        user = self._users_by_id.get(id)
        if user is None:
            raise UsuarioNoEncontrado(str(id))
        return user


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.user_repo = FakeUserRepository()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


def make_register_dto(
    *,
    fullname: str = "Test User",
    email: str = "test@example.com",
    password: str = "TestPassword123!",
    contact_number: str = "300123456",
    role: RolUsuario = RolUsuario.LECTOR,
) -> RegisterUserDto:
    return RegisterUserDto(
        fullname=fullname,
        email=email,
        password=password,
        contact_number=contact_number,
        role=role,
    )


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService(FakeUnitOfWork())


class TestValidateUser:
    @pytest.mark.anyio
    async def test_returns_token_for_valid_credentials(self, auth_service: AuthService):
        dto = make_register_dto(email="reader@example.com", password="SecurePass123!")
        await auth_service.registerUser(dto)

        token = await auth_service.validateUser(dto.email, "SecurePass123!")

        assert isinstance(token, str)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["role"] == str(RolUsuario.LECTOR)
        assert payload["iss"] == "LookOwl-Server"

    @pytest.mark.anyio
    async def test_returns_none_for_invalid_password(self, auth_service: AuthService):
        dto = make_register_dto(email="reader2@example.com", password="SecurePass123!")
        await auth_service.registerUser(dto)

        token = await auth_service.validateUser(dto.email, "wrong-password")

        assert token is None

    @pytest.mark.anyio
    async def test_returns_none_for_unknown_user(self, auth_service: AuthService):
        with pytest.raises(UsuarioNoEncontrado):
            await auth_service.validateUser("missing@example.com", "any-password")


class TestValidateToken:
    @pytest.mark.anyio
    async def test_returns_user_by_token_subject(self, auth_service: AuthService):
        dto = make_register_dto(email="token-user@example.com", password="TokenPass123!")
        created_user = await auth_service.registerUser(dto)
        token = generate_token(user_id=str(created_user.uid), user_role=str(created_user.role))

        resolved_user = await auth_service.validateToken(token)

        assert resolved_user is not None
        assert resolved_user.uid == created_user.uid
        assert resolved_user.email == created_user.email


class TestRegisterUser:
    @pytest.mark.anyio
    async def test_creates_user_with_hashed_password(self, auth_service: AuthService):
        dto = make_register_dto(email="new-user@example.com", password="PlainText123!")

        created_user = await auth_service.registerUser(dto)

        assert created_user.email == dto.email
        assert created_user.full_name == dto.fullname
        assert created_user.role == RolUsuario.LECTOR
        assert created_user.uid == 1
        assert dto.password != "PlainText123!"
        assert verify_password("PlainText123!", dto.password)

    @pytest.mark.anyio
    async def test_raises_unknown_exception_when_email_already_exists(self, auth_service: AuthService):
        dto = make_register_dto(email="duplicate@example.com", password="PlainText123!")
        await auth_service.registerUser(dto)

        duplicate_dto = make_register_dto(email="duplicate@example.com", password="OtherPass456!")

        with pytest.raises(UnknownException):
            await auth_service.registerUser(duplicate_dto)

    @pytest.mark.anyio
    async def test_registered_user_can_authenticate(self, auth_service: AuthService):
        dto = make_register_dto(email="flow@example.com", password="FlowPass123!")

        created_user = await auth_service.registerUser(dto)
        token = await auth_service.validateUser(created_user.email, "FlowPass123!")

        assert token is not None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == str(created_user.uid)
        assert payload["role"] == str(created_user.role)


class TestPasswordHelpers:
    def test_hash_password_changes_value(self):
        hashed = hash_password("SamePassword123!")

        assert hashed != "SamePassword123!"

    def test_verify_password_matches_plaintext(self):
        hashed = hash_password("Secret123!")

        assert verify_password("Secret123!", hashed) is True
        assert verify_password("Wrong123!", hashed) is False
