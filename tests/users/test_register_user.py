from unittest.mock import AsyncMock, MagicMock

import pytest

from users.application.use_cases.register_user import RegisterUser
from users.domain.user import UserRole
from users.domain.user_credential import HashedPassword


class TestRegisterUser:

    @pytest.mark.asyncio
    async def test_register_user_successfully(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        fake_uow,
    ) -> None:
        # Arrange
        hashed = HashedPassword("hashed_abc")
        mock_password_hasher.hash_password.return_value = hashed

        uc = RegisterUser(mock_user_repo, mock_password_hasher, fake_uow)

        # Act
        await uc.execute(
            full_name="Juan Pérez",
            contact_number="555-1234",
            email="juan@lib.edu",
            password="secret123",
        )

        # Assert
        mock_password_hasher.hash_password.assert_called_once_with("secret123")
        mock_user_repo.save_user.assert_called_once()
        saved_user = mock_user_repo.save_user.call_args[0][0]
        assert saved_user.full_name == "Juan Pérez"
        assert saved_user.contact_number == "555-1234"
        assert saved_user.role == UserRole.LECTOR
        assert saved_user.credentials.email == "juan@lib.edu"
        assert saved_user.credentials.stored_password == hashed
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_register_user_always_creates_as_lector(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        fake_uow,
    ) -> None:
        """Verify that RegisterUser always assigns the LECTOR role,
        regardless of input."""
        # Arrange
        mock_password_hasher.hash_password.return_value = HashedPassword("hashed")
        uc = RegisterUser(mock_user_repo, mock_password_hasher, fake_uow)

        # Act
        await uc.execute(
            full_name="Admin User",
            contact_number="555-9999",
            email="admin@lib.edu",
            password="admin123",
        )

        # Assert
        saved_user = mock_user_repo.save_user.call_args[0][0]
        assert saved_user.role == UserRole.LECTOR

    @pytest.mark.asyncio
    async def test_register_user_rolls_back_on_save_failure(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_password_hasher.hash_password.return_value = HashedPassword("hashed")
        mock_user_repo.save_user.side_effect = RuntimeError("DB error")

        uc = RegisterUser(mock_user_repo, mock_password_hasher, fake_uow)

        # Act & Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await uc.execute(
                full_name="Fail User",
                contact_number="555-0000",
                email="fail@lib.edu",
                password="pass",
            )

        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_register_user_hashes_password_before_saving(
        self,
        mock_user_repo: AsyncMock,
        mock_password_hasher: MagicMock,
        fake_uow,
    ) -> None:
        """Ensure the raw password is never passed directly to the repository."""
        # Arrange
        mock_password_hasher.hash_password.return_value = HashedPassword("hashed_xyz")
        uc = RegisterUser(mock_user_repo, mock_password_hasher, fake_uow)

        # Act
        await uc.execute(
            full_name="Safe User",
            contact_number="555-1111",
            email="safe@lib.edu",
            password="raw_password",
        )

        # Assert
        saved_user = mock_user_repo.save_user.call_args[0][0]
        assert saved_user.credentials.stored_password.hashed == "hashed_xyz"
        # The raw password should never appear in the saved user
        assert "raw_password" not in str(saved_user)
