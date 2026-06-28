from unittest.mock import AsyncMock, MagicMock

import pytest

from users.application.use_cases.login_user import LoginUser
from users.domain.token import EncryptedToken
from users.domain.user import User
from users.domain.user_credential import HashedPassword, UserCredentials
from users.domain.user_id import UserId
from users.domain.user_role import UserRole


def _make_user(user_id: int, email: str, role: UserRole = UserRole.LECTOR) -> User:
    return User(
        id=UserId(user_id),
        full_name="Test User",
        contact_number="555-0000",
        role=role,
        credentials=UserCredentials(
            email=email,
            stored_password=HashedPassword("stored_hash"),
        ),
    )


class TestLoginUser:

    @pytest.mark.asyncio
    async def test_login_successfully_returns_token(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_handler: MagicMock,
        fake_uow,
    ) -> None:
        # Arrange
        user = _make_user(1, "juan@lib.edu")
        stored_credentials = UserCredentials(
            email="juan@lib.edu",
            stored_password=HashedPassword("stored_hash"),
        )
        expected_token = EncryptedToken("jwt.token.here")

        mock_user_repo.find_user_credential.return_value = stored_credentials
        mock_password_hasher.verify_password.return_value = True
        mock_user_repo.get_by_email.return_value = user
        mock_token_handler.generate_token.return_value = expected_token

        uc = LoginUser(mock_user_repo, mock_password_hasher, mock_token_handler, fake_uow)

        # Act
        result = await uc.execute(email="juan@lib.edu", password="secret123")

        # Assert
        assert result == expected_token
        assert result.raw_value == "jwt.token.here"
        assert fake_uow.committed
        mock_password_hasher.verify_password.assert_called_once_with(
            stored_credentials.stored_password, "secret123"
        )
        mock_token_handler.generate_token.assert_called_once_with(
            user_id=user.id, user_role=user.role
        )

    @pytest.mark.asyncio
    async def test_login_raises_when_credentials_not_found(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_handler: MagicMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_user_repo.find_user_credential.return_value = None

        uc = LoginUser(mock_user_repo, mock_password_hasher, mock_token_handler, fake_uow)

        # Act & Assert
        with pytest.raises(Exception, match="No credentials found"):
            await uc.execute(email="unknown@lib.edu", password="pass")

        mock_token_handler.generate_token.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_login_raises_when_password_does_not_match(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_handler: MagicMock,
        fake_uow,
    ) -> None:
        # Arrange
        stored_credentials = UserCredentials(
            email="juan@lib.edu",
            stored_password=HashedPassword("stored_hash"),
        )
        mock_user_repo.find_user_credential.return_value = stored_credentials
        mock_password_hasher.verify_password.return_value = False

        uc = LoginUser(mock_user_repo, mock_password_hasher, mock_token_handler, fake_uow)

        # Act & Assert
        with pytest.raises(Exception, match="Invalid password"):
            await uc.execute(email="juan@lib.edu", password="wrong_password")

        mock_token_handler.generate_token.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_login_raises_when_user_not_found_by_email(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_handler: MagicMock,
        fake_uow,
    ) -> None:
        # Arrange
        stored_credentials = UserCredentials(
            email="juan@lib.edu",
            stored_password=HashedPassword("stored_hash"),
        )
        mock_user_repo.find_user_credential.return_value = stored_credentials
        mock_password_hasher.verify_password.return_value = True
        mock_user_repo.get_by_email.return_value = None  # user gone after auth check

        uc = LoginUser(mock_user_repo, mock_password_hasher, mock_token_handler, fake_uow)

        # Act & Assert
        with pytest.raises(Exception, match="No user found"):
            await uc.execute(email="juan@lib.edu", password="secret123")

        mock_token_handler.generate_token.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_login_generates_token_with_correct_role(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_token_handler: MagicMock,
        fake_uow,
    ) -> None:
        """Verify the token is generated with the user's actual role."""
        # Arrange
        librarian = _make_user(2, "biblio@lib.edu", role=UserRole.BIBLIOTECARIO)
        stored_credentials = UserCredentials(
            email="biblio@lib.edu",
            stored_password=HashedPassword("hash"),
        )
        mock_user_repo.find_user_credential.return_value = stored_credentials
        mock_password_hasher.verify_password.return_value = True
        mock_user_repo.get_by_email.return_value = librarian
        mock_token_handler.generate_token.return_value = EncryptedToken("token")

        uc = LoginUser(mock_user_repo, mock_password_hasher, mock_token_handler, fake_uow)

        # Act
        await uc.execute(email="biblio@lib.edu", password="pass")

        # Assert
        mock_token_handler.generate_token.assert_called_once_with(
            user_id=UserId(2), user_role=UserRole.BIBLIOTECARIO
        )
