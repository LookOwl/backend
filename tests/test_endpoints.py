import os
import sys
import types
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/test")
os.environ.setdefault("ASYNC_DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


if "sentence_transformers" not in sys.modules:
    sentence_transformers_stub = types.ModuleType("sentence_transformers")

    class _FakeSentenceTransformer:
        def __init__(self, *args, **kwargs):
            pass

        def encode(self, text):
            return [0.0]

    sentence_transformers_stub.SentenceTransformer = _FakeSentenceTransformer
    sys.modules["sentence_transformers"] = sentence_transformers_stub


from core.security import ALGORITHM, SECRET_KEY, generate_token, hash_password, verify_password
from core.auth_guard import user_auth_guard
from api.controllers.books import router as books_router
from api.controllers.users import router as users_router
from dependencies.services import get_auth_service, get_book_service
from domain.book import Book
from domain.enums.roles_usuario import RolUsuario
from domain.user import User, UserCredentials
from services.auth_service import UserAlreadyExistsException


app = FastAPI()
app.include_router(users_router, prefix="/api")
app.include_router(books_router, prefix="/api")


class FakeAuthService:
    def __init__(self) -> None:
        self._users_by_email: dict[str, User] = {}
        self._users_by_id: dict[int, User] = {}
        self._next_id = 1

    async def registerUser(self, registerDto):
        if registerDto.email in self._users_by_email:
            raise UserAlreadyExistsException()

        stored_user = User(
            uid=self._next_id,
            full_name=registerDto.fullname,
            email=registerDto.email,
            contact_number=registerDto.contact_number,
            role=registerDto.role,
            credentials=UserCredentials(password_hash=hash_password(registerDto.password)),
        )
        self._next_id += 1
        self._users_by_email[stored_user.email] = stored_user
        self._users_by_id[stored_user.uid] = stored_user
        registerDto.password = stored_user.credentials.password_hash
        return stored_user

    async def validateUser(self, email: str, password: str):
        user = self._users_by_email.get(email)
        if user is None:
            return None
        if not verify_password(password, user.credentials.password_hash):
            return None
        return generate_token(user_id=str(user.uid), user_role=str(user.role))

    async def validateToken(self, token: str):
        from core.security import decode_token

        payload = decode_token(token)
        return self._users_by_id.get(int(payload["sub"]))


class FakeBookService:
    def __init__(self) -> None:
        self.registered_books = []

    async def getBooks(self, searchDto):
        return [
            Book(
                id=1,
                title="Clean Architecture",
                isbn="9780134494166",
                description="A classic architecture book",
                editorial="Prentice Hall",
                publication_date=date(2017, 9, 20),
                cover_url="https://example.com/cover.jpg",
                language="es",
                author=["Robert C. Martin"],
                category=["Software"],
                page_count=432,
            ),
            Book(
                id=2,
                title="Domain-Driven Design",
                isbn="9780321125217",
                description="Modeling complex software",
                editorial="Addison-Wesley",
                publication_date=date(2003, 8, 30),
                cover_url="https://example.com/ddd.jpg",
                language="es",
                author=["Eric Evans"],
                category=["Software"],
                page_count=560,
            ),
        ]

    async def registerBook(self, bookDto):
        self.registered_books.append(bookDto)
        return 42


@pytest.fixture
def fake_auth_service():
    return FakeAuthService()


@pytest.fixture
def fake_book_service():
    return FakeBookService()


@pytest.fixture
def librarian_user():
    return User(
        uid=99,
        full_name="Librarian",
        email="librarian@test.com",
        contact_number="300123456",
        role=RolUsuario.BIBLIOTECARIO,
        credentials=UserCredentials(password_hash="unused"),
    )


@pytest.fixture
def regular_user():
    return User(
        uid=100,
        full_name="Reader",
        email="reader@test.com",
        contact_number="300123457",
        role=RolUsuario.LECTOR,
        credentials=UserCredentials(password_hash="unused"),
    )


@pytest.fixture
def client(fake_auth_service, fake_book_service, librarian_user):
    app.dependency_overrides[get_auth_service] = lambda: fake_auth_service
    app.dependency_overrides[get_book_service] = lambda: fake_book_service
    app.dependency_overrides[user_auth_guard] = lambda: librarian_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_register_user_endpoint(client):
    response = client.post(
        "/api/users/register",
        json={
            "fullname": "Test User",
            "contact_number": "300123456",
            "email": "register@test.com",
            "password": "TestPassword123!",
            "role": "lector",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {"user_id": 1, "role": "lector"}


def test_login_user_endpoint_returns_token(client):
    client.post(
        "/api/users/register",
        json={
            "fullname": "Login User",
            "contact_number": "300123456",
            "email": "login@test.com",
            "password": "SecurePass123!",
            "role": "lector",
        },
    )

    response = client.post(
        "/api/users/login",
        json={"email": "login@test.com", "password": "SecurePass123!", "role": "lector"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_login_user_endpoint_rejects_invalid_credentials(client):
    response = client.post(
        "/api/users/login",
        json={"email": "missing@test.com", "password": "WrongPass123!", "role": "lector"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_register_book_endpoint_authorized_success(client, fake_book_service):
    response = client.post(
        "/api/books/register",
        headers={"Authorization": "Bearer fake-token"},
        json={
            "title": "Clean Architecture",
            "isbn": "9780134494166",
            "description": "Architecture for maintainable systems",
            "editorial": "Prentice Hall",
            "publication_date": str(date(2026, 5, 4)),
            "cover_url": "https://example.com/cover.jpg",
            "language": "es",
            "author": ["Robert C. Martin"],
            "category": ["Software"],
            "page_count": 432,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"id": 42}
    assert len(fake_book_service.registered_books) == 1


def test_register_book_endpoint_rejects_non_librarian(fake_auth_service, fake_book_service, regular_user):
    app.dependency_overrides[get_auth_service] = lambda: fake_auth_service
    app.dependency_overrides[get_book_service] = lambda: fake_book_service
    app.dependency_overrides[user_auth_guard] = lambda: regular_user

    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/books/register",
            headers={"Authorization": "Bearer fake-token"},
            json={
                "title": "Clean Architecture",
                "isbn": "9780134494166",
                "description": "Architecture for maintainable systems",
                "editorial": "Prentice Hall",
                "publication_date": str(date(2026, 5, 4)),
                "cover_url": "https://example.com/cover.jpg",
                "language": "es",
                "author": ["Robert C. Martin"],
                "category": ["Software"],
                "page_count": 432,
            },
        )

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Sólo bibliotecarios autorizados"


def test_get_books_endpoint_paginates(client):
    response = client.get("/api/books/?limit=1&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["title"] == "Clean Architecture"
    assert body["page"]["has_next"] is True
    assert body["page"]["next_cursor"] == {"offset": 1}