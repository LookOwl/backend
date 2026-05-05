import os
from datetime import date
import types

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from api.core.security import generate_token, hash_password
from api.services.auth_service import AuthService
from api.services.exports.di import get_auth_service, get_book_service
from domain.user import User, UserCredentials
from main import app
from repositories.exports.di import get_user_repository


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, object] = {}
        self.count = 0

    async def saveUser(self, user):
        for user_id, existing_user in self.users.items():
            if existing_user.email == user.email:
                raise Exception(f"Correo ya registrado por usuario con id: {user_id}")
        self.users[str(self.count)] = user
        self.count += 1

    async def getUserCredentials(self, email: str) -> UserCredentials | None:
        for user_id, user in self.users.items():
            if user.email == email:
                return UserCredentials(
                    uid=str(user_id),
                    email=user.email,
                    password=user.password,
                    role="User",
                )
        return None

    async def findUserById(self, user_id: str) -> User | None:
        user = self.users.get(str(user_id))
        if user is None:
            return None
        return User(
            uid=str(user_id),
            full_name=user.fullname,
            contact_number=user.contact_number,
            role="User",
        )


class FakeBookService:
    def __init__(self) -> None:
        self.last_book = None

    async def registerBook(self, book):
        self.last_book = book
        return 42


@pytest.fixture
def fake_user_repo():
    return FakeUserRepository()


@pytest.fixture
def fake_book_service():
    return FakeBookService()


@pytest.fixture
def client(fake_user_repo, fake_book_service):
    app.dependency_overrides[get_user_repository] = lambda: fake_user_repo
    app.dependency_overrides[get_auth_service] = lambda: AuthService(fake_user_repo)
    app.dependency_overrides[get_book_service] = lambda: fake_book_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_register_user_endpoint(client):
    response = client.post(
        "/api/users/register",
        json={
            "fullname": "Test User",
            "contact_number": 1234567890,
            "email": "register@test.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "Test User" in body
    assert "register@test.com" in body
    assert "TestPassword123!" not in body
    assert "password" not in body.lower()


def test_login_user_endpoint_returns_token(client):
    client.post(
        "/api/users/register",
        json={
            "fullname": "Login User",
            "contact_number": 987654321,
            "email": "login@test.com",
            "password": "SecurePass123!",
        },
    )

    response = client.post(
        "/api/users/login",
        json={"email": "login@test.com", "password": "SecurePass123!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


def test_login_user_endpoint_rejects_invalid_credentials(client):
    response = client.post(
        "/api/users/login",
        json={"email": "missing@test.com", "password": "WrongPass123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_register_book_endpoint_authorized_success(client, fake_user_repo):
    fake_user = types.SimpleNamespace(
        fullname="Authorized User",
        contact_number=555000111,
        email="auth@test.com",
        password=hash_password("AuthPass123!"),
    )
    fake_user_repo.users["0"] = fake_user
    token = generate_token("0", "User")

    response = client.post(
        "/api/catalog/register",
        headers={"Authorization": f"Bearer {token}"},
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
