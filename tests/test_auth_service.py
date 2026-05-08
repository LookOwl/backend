import pytest
import jwt
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from services.auth_service import AuthService
from api.dtos.login_dto import LoginDto, RegisterUserDto
from core.security import (
    hash_password,
    verify_password,
    generate_token,
    SECRET_KEY,
    ALGORITHM,
)
from domain.user import UserCredentials


class MockUserRepository:

    def __init__(self):
        self.users: dict[str, RegisterUserDto] = {}
        self.count = 0

    async def saveUser(self, user: RegisterUserDto):
        for id, existing_user in self.users.items():
            if existing_user.email == user.email:
                raise Exception(f"Correo ya registrado por usuario con id: {id}")
        self.users[str(self.count)] = user
        self.count += 1

    async def getUserCredentials(self, email: str) -> UserCredentials | None:
        for id, u in self.users.items():
            if u.email == email:
                return UserCredentials(
                    uid=str(id),
                    email=u.email,
                    password=u.password,
                    role="User",
                )
        return None


def create_test_user(
    email: str = "test@example.com",
    password: str = "TestPassword123!",
    fullname: str = "Test User",
    contact_number: int = 1234567890,
) -> tuple[RegisterUserDto, str]:
    dto = RegisterUserDto(
        fullname=fullname,
        email=email,
        password=password,
        contact_number=contact_number,
    )
    return dto, password


@pytest.fixture
def mock_repo():
    """Fixture que proporciona un repositorio de usuario simulado"""
    return MockUserRepository()


@pytest.fixture
def auth_service(mock_repo):
    """Fixture que proporciona AuthService con repositorio simulado"""
    return AuthService(mock_repo)


class TestValidateUser:
    """Pruebas para el método AuthService.validateUser()"""

    @pytest.mark.anyio
    async def test_validar_usuario_exitoso_con_credenciales_correctas(
        self, auth_service, mock_repo
    ):
        """Prueba de inicio de sesión exitoso con correo y contraseña correctos"""
        # Preparar
        email = "user@test.com"
        password = "SecurePass123!"
        user_dto, _ = create_test_user(email=email, password=password)

        # Registrar usuario primero
        hashed_password = hash_password(password)
        user_dto.password = hashed_password
        await mock_repo.saveUser(user_dto)

        # Actuar
        token = await auth_service.validateUser(email, password)

        # Verificar
        assert token is not None
        assert isinstance(token, str)
        # Verificar que el token es un JWT válido
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "0"  # ID de usuario simulado
        assert decoded["role"] == "User"

    @pytest.mark.anyio
    async def test_validar_usuario_falla_con_contrasena_incorrecta(
        self, auth_service, mock_repo
    ):
        """Prueba de fallo de inicio de sesión cuando la contraseña es incorrecta"""
        # Preparar
        email = "user@test.com"
        password = "CorrectPass123!"
        wrong_password = "WrongPass456!"
        user_dto, _ = create_test_user(email=email, password=password)

        # Registrar usuario con contraseña correcta
        hashed_password = hash_password(password)
        user_dto.password = hashed_password
        await mock_repo.saveUser(user_dto)

        # Actuar
        token = await auth_service.validateUser(email, wrong_password)

        # Verificar
        assert token is None

    @pytest.mark.anyio
    async def test_validar_usuario_falla_con_usuario_inexistente(self, auth_service):
        """Prueba de fallo de inicio de sesión cuando el usuario no existe"""
        # Actuar
        token = await auth_service.validateUser("nonexistent@test.com", "anypass")

        # Verificar
        assert token is None

    @pytest.mark.anyio
    async def test_validar_usuario_falla_con_credenciales_vacias(self, auth_service):
        """Prueba de fallo de inicio de sesión con correo o contraseña vacíos"""
        # Actuar
        token = await auth_service.validateUser("", "password")

        # Verificar
        assert token is None

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "email,password",
        [
            ("user1@test.com", "Pass123!"),
            ("user2@test.com", "AnotherPass456!"),
            ("admin@test.com", "AdminPass789!"),
        ],
    )
    async def test_validar_usuario_con_multiples_usuarios(
        self, auth_service, mock_repo, email, password
    ):
        """Prueba de que cada usuario pueda iniciar sesión con sus propias credenciales"""
        # Preparar
        for i, (test_email, test_password) in enumerate(
            [
                ("user1@test.com", "Pass123!"),
                ("user2@test.com", "AnotherPass456!"),
                ("admin@test.com", "AdminPass789!"),
            ]
        ):
            user_dto, _ = create_test_user(
                email=test_email, password=test_password, fullname=f"User {i+1}"
            )
            hashed_password = hash_password(test_password)
            user_dto.password = hashed_password
            await mock_repo.saveUser(user_dto)

        # Actuar
        token = await auth_service.validateUser(email, password)

        # Verificar
        assert token is not None
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["role"] == "User"


class TestRegisterUser:
    """Pruebas para el método AuthService.registerUser()"""

    @pytest.mark.anyio
    async def test_registrar_usuario_exitoso(self, auth_service):
        """Prueba de registro de usuario exitoso"""
        # Preparar
        user_dto, _ = create_test_user(
            email="newuser@test.com", fullname="New User"
        )

        # Actuar
        result = await auth_service.registerUser(user_dto)

        # Verificar
        assert result is True
        assert user_dto.password != "TestPassword123!"  # La contraseña debe estar cifrada

    @pytest.mark.anyio
    async def test_registrar_usuario_falla_con_correo_duplicado(
        self, auth_service, mock_repo
    ):
        """Prueba de fallo de registro cuando el correo ya existe"""
        # Preparar
        email = "duplicate@test.com"
        user_dto1, password1 = create_test_user(email=email, fullname="User 1")
        user_dto2, password2 = create_test_user(email=email, fullname="User 2")

        # Registrar primer usuario
        await auth_service.registerUser(user_dto1)

        # Actuar - Intentar registrar segundo usuario con el mismo correo
        result = await auth_service.registerUser(user_dto2)

        # Verificar
        assert result is False

    @pytest.mark.anyio
    async def test_registrar_usuario_contrasena_cifrada(self, auth_service, mock_repo):
        """Prueba de que la contraseña se cifre correctamente durante el registro"""
        # Preparar
        password = "PlainTextPassword123!"
        user_dto, _ = create_test_user(email="test@test.com", password=password)

        # Actuar
        await auth_service.registerUser(user_dto)
        registered_user = await mock_repo.getUserCredentials("test@test.com")

        # Verificar
        assert registered_user is not None
        assert registered_user.password != password  # La contraseña debe estar cifrada
        assert verify_password(password, registered_user.password)  # La verificación funciona

    @pytest.mark.anyio
    async def test_registrar_usuario_e_iniciar_sesion(self, auth_service, mock_repo):
        """Prueba del flujo completo: registrar usuario e iniciar sesión"""
        # Preparar
        email = "complete@test.com"
        password = "CompleteFlow123!"
        user_dto, _ = create_test_user(email=email, password=password)

        # Actuar - Registrar usuario
        register_result = await auth_service.registerUser(user_dto)

        # Actuar - Iniciar sesión con credenciales registradas
        token = await auth_service.validateUser(email, password)

        # Verificar
        assert register_result is True
        assert token is not None
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["role"] == "User"


class TestTokenGeneration:
    """Pruebas para la generación de tokens JWT"""

    @pytest.mark.anyio
    async def test_token_contiene_id_usuario(self, auth_service, mock_repo):
        """Prueba de que el token generado contiene la ID del usuario"""
        # Preparar
        email = "token@test.com"
        password = "TokenPass123!"
        user_dto, _ = create_test_user(email=email, password=password)

        hashed_password = hash_password(password)
        user_dto.password = hashed_password
        await mock_repo.saveUser(user_dto)

        # Actuar
        token = await auth_service.validateUser(email, password)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar
        assert "sub" in decoded  # Asunto (id_usuario)
        assert decoded["sub"] == "0"

    @pytest.mark.anyio
    async def test_token_contiene_rol_usuario(self, auth_service, mock_repo):
        """Prueba de que el token generado contiene el rol del usuario"""
        # Preparar
        email = "role@test.com"
        password = "RolePass123!"
        user_dto, _ = create_test_user(email=email, password=password)

        hashed_password = hash_password(password)
        user_dto.password = hashed_password
        await mock_repo.saveUser(user_dto)

        # Actuar
        token = await auth_service.validateUser(email, password)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar
        assert "role" in decoded
        assert decoded["role"] == "User"

    @pytest.mark.anyio
    async def test_token_tiene_expiracion(self, auth_service, mock_repo):
        """Prueba de que el token generado tiene tiempo de expiración"""
        # Preparar
        email = "expiry@test.com"
        password = "ExpiryPass123!"
        user_dto, _ = create_test_user(email=email, password=password)

        hashed_password = hash_password(password)
        user_dto.password = hashed_password
        await mock_repo.saveUser(user_dto)

        # Actuar
        token = await auth_service.validateUser(email, password)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar
        assert "exp" in decoded
        assert "iat" in decoded
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        assert exp_time > now  # El token debe expirar en el futuro

    @pytest.mark.anyio
    async def test_token_emisor_correcto(self, auth_service, mock_repo):
        """Prueba de que el token tiene el emisor correcto"""
        # Preparar
        email = "issuer@test.com"
        password = "IssuerPass123!"
        user_dto, _ = create_test_user(email=email, password=password)

        hashed_password = hash_password(password)
        user_dto.password = hashed_password
        await mock_repo.saveUser(user_dto)

        # Actuar
        token = await auth_service.validateUser(email, password)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar
        assert decoded["iss"] == "LookOwl-Server"


class TestPasswordHashing:
    """Pruebas para el cifrado y verificación de contraseña"""

    def test_cifrar_contrasena_produce_diferentes_hashes(self):
        """Prueba de que la misma contraseña produce diferentes hashes (debido a salt)"""
        password = "MyPassword123!"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Diferentes hashes debido a salt aleatorio

    def test_verificar_contrasena_exitosa_con_correcta(self):
        """Prueba de verificación de contraseña con contraseña correcta"""
        password = "CorrectPassword123!"
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verificar_contrasena_falla_con_incorrecta(self):
        """Prueba de verificación de contraseña con contraseña incorrecta"""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        result = verify_password(wrong_password, hashed)

        assert result is False

    @pytest.mark.parametrize(
        "password",
        [
            "SimplePassword",
            "P@ssw0rd!",
            "VeryLongPasswordWith123456789",
            "1234567890",
            "!@#$%^&*()",
        ],
    )
    def test_verificar_contrasena_con_varios_formatos(self, password):
        """Prueba de verificación de contraseña con varios formatos de contraseña"""
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True
