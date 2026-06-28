from datetime import date
from unittest.mock import AsyncMock

import pytest

from books.application.use_cases.register_book import RegisterBook
from books.domain.book import BookISBN, BookLanguage
from users.domain.user import User
from users.domain.user_credential import HashedPassword, UserCredentials
from users.domain.user_id import UserId
from users.domain.user_role import UserRole


def _make_librarian(user_id: int = 1) -> User:
    return User(
        id=UserId(user_id),
        full_name="Bibliotecario Pérez",
        contact_number="555-0001",
        role=UserRole.BIBLIOTECARIO,
        credentials=UserCredentials(
            email="biblio@lib.edu",
            stored_password=HashedPassword("hashed"),
        ),
    )


def _make_reader(user_id: int = 2) -> User:
    return User(
        id=UserId(user_id),
        full_name="Lector López",
        contact_number="555-0002",
        role=UserRole.LECTOR,
        credentials=UserCredentials(
            email="lector@lib.edu",
            stored_password=HashedPassword("hashed"),
        ),
    )


class TestRegisterBook:

    @pytest.mark.asyncio
    async def test_register_book_successfully_as_librarian(
        self, mock_book_repo: AsyncMock, mock_user_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        librarian = _make_librarian(1)
        mock_user_repo.get_by_id.return_value = librarian
        uc = RegisterBook(mock_book_repo, mock_user_repo, fake_uow)

        # Act
        await uc.execute(
            title="Cien Años de Soledad",
            isbn="978-0307474728",
            description="Obra maestra del realismo mágico",
            editorial="Sudamericana",
            publication_date=date(1967, 6, 5),
            cover_url="http://covers.example.com/cien-anos.jpg",
            language="es",
            author=["Gabriel García Márquez"],
            category=["Ficción", "Realismo mágico"],
            page_count=471,
            user_id=1,
        )

        # Assert
        mock_book_repo.save_book.assert_called_once()
        saved_book = mock_book_repo.save_book.call_args[0][0]
        assert saved_book.title.title == "Cien Años de Soledad"
        assert saved_book.isbn.isbn_code == "978-0307474728"
        assert saved_book.author.authors == ["Gabriel García Márquez"]
        assert saved_book.category.categories == ["Ficción", "Realismo mágico"]
        assert saved_book.page_count.count == 471
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_register_book_raises_when_user_not_found(
        self, mock_book_repo: AsyncMock, mock_user_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        mock_user_repo.get_by_id.return_value = None
        uc = RegisterBook(mock_book_repo, mock_user_repo, fake_uow)

        # Act & Assert
        with pytest.raises(Exception, match="User not found"):
            await uc.execute(
                title="Any Book",
                isbn="978-0000000001",
                description="desc",
                editorial="ed",
                publication_date=date(2020, 1, 1),
                cover_url="http://x.com/img.jpg",
                language="en",
                author=["Author"],
                category=["Cat"],
                page_count=100,
                user_id=99,
            )

        mock_book_repo.save_book.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_register_book_raises_when_user_is_not_librarian(
        self, mock_book_repo: AsyncMock, mock_user_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        reader = _make_reader(2)
        mock_user_repo.get_by_id.return_value = reader
        uc = RegisterBook(mock_book_repo, mock_user_repo, fake_uow)

        # Act & Assert
        with pytest.raises(Exception, match="Only librarians can create books"):
            await uc.execute(
                title="Any Book",
                isbn="978-0000000001",
                description="desc",
                editorial="ed",
                publication_date=date(2020, 1, 1),
                cover_url="http://x.com/img.jpg",
                language="en",
                author=["Author"],
                category=["Cat"],
                page_count=100,
                user_id=2,
            )

        mock_book_repo.save_book.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_register_book_with_minimal_fields(
        self, mock_book_repo: AsyncMock, mock_user_repo: AsyncMock, fake_uow
    ) -> None:
        """Register a book providing only the required fields."""
        # Arrange
        librarian = _make_librarian(1)
        mock_user_repo.get_by_id.return_value = librarian
        uc = RegisterBook(mock_book_repo, mock_user_repo, fake_uow)

        # Act
        await uc.execute(
            title="1984",
            isbn="978-0451524935",
            description="Distopía clásica",
            editorial="Secker & Warburg",
            publication_date=date(1949, 6, 8),
            cover_url="http://covers.example.com/1984.jpg",
            language="en",
            author=["George Orwell"],
            category=["Ficción", "Distopía"],
            page_count=328,
            user_id=1,
        )

        # Assert
        mock_book_repo.save_book.assert_called_once()
        assert fake_uow.committed

    @pytest.mark.asyncio
    async def test_register_book_rolls_back_on_save_failure(
        self, mock_book_repo: AsyncMock, mock_user_repo: AsyncMock, fake_uow
    ) -> None:
        # Arrange
        librarian = _make_librarian(1)
        mock_user_repo.get_by_id.return_value = librarian
        mock_book_repo.save_book.side_effect = RuntimeError("DB error")
        uc = RegisterBook(mock_book_repo, mock_user_repo, fake_uow)

        # Act & Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await uc.execute(
                title="Failing Book",
                isbn="978-0000000001",
                description="desc",
                editorial="ed",
                publication_date=date(2020, 1, 1),
                cover_url="http://x.com/img.jpg",
                language="en",
                author=["Author"],
                category=["Cat"],
                page_count=100,
                user_id=1,
            )

        assert not fake_uow.committed
