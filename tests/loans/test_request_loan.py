from datetime import date
from unittest.mock import AsyncMock

import pytest

from books.domain.book import (
    Book,
    BookAuthor,
    BookCategory,
    BookDescription,
    BookId,
    BookLanguage,
    BookTitle,
)
from books.domain.book_availability import BookAvailability
from loans.application.use_cases.request_loan import RequestLoan
from loans.domain.loan_request_status import LoanRequestStatus
from users.domain.user import User
from users.domain.user_credential import HashedPassword, UserCredentials
from users.domain.user_id import UserId
from users.domain.user_role import UserRole


def _make_user(user_id: int, role: UserRole = UserRole.LECTOR) -> User:
    return User(
        id=UserId(user_id),
        full_name="Test User",
        contact_number="555-0000",
        role=role,
        credentials=UserCredentials(
            email="test@lib.edu",
            stored_password=HashedPassword("hashed"),
        ),
    )


def _make_book(book_id: int, title: str = "Test Book") -> Book:
    return Book(
        book_id=BookId(book_id),
        title=BookTitle(title),
        isbn=None,
        description=BookDescription("desc"),
        editorial=None,
        publication_date=None,
        cover_url=None,
        language=BookLanguage("es"),
        author=BookAuthor(["Author"]),
        category=BookCategory(["Category"]),
        page_count=None,
    )


class TestRequestLoan:

    @pytest.mark.asyncio
    async def test_request_loan_successfully(
        self,
        mock_book_repo: AsyncMock,
        mock_user_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        user = _make_user(1)
        book = _make_book(10)
        mock_user_repo.get_by_id.return_value = user
        mock_book_repo.get_by_id.return_value = book
        mock_book_availability_facade.read_availability.return_value = (
            BookAvailability(book_id=book.book_id, no_soft_locked_copies=3, no_hard_locked_copies=2)
        )

        uc = RequestLoan(
            fake_uow,
            mock_loan_req_repo,
            mock_book_repo,
            mock_user_repo,
            mock_book_availability_facade,
            mock_loan_event_dispatcher,
        )

        # Act
        result = await uc.execute(
            user_id=1, book_id=10, max_interest_time=48, requested_loan_time=14
        )

        # Assert
        assert result is True  # queue_length > 0 → privileged
        assert fake_uow.committed
        mock_loan_req_repo.save_request.assert_called_once()
        mock_loan_event_dispatcher.notify.assert_called_once()

        # Verify the saved request has correct fields
        saved_request = mock_loan_req_repo.save_request.call_args[0][0]
        assert saved_request.user_id.uid == 1
        assert saved_request.book_id.id == 10
        assert saved_request.status == LoanRequestStatus.PENDIENTE
        assert saved_request.wait_time.time == 48
        assert saved_request.loan_time.time == 14

    @pytest.mark.asyncio
    async def test_request_loan_returns_false_when_no_copies_available(
        self,
        mock_book_repo: AsyncMock,
        mock_user_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        user = _make_user(1)
        book = _make_book(10)
        mock_user_repo.get_by_id.return_value = user
        mock_book_repo.get_by_id.return_value = book
        mock_book_availability_facade.read_availability.return_value = (
            BookAvailability(book_id=book.book_id, no_soft_locked_copies=0, no_hard_locked_copies=0)
        )

        uc = RequestLoan(
            fake_uow,
            mock_loan_req_repo,
            mock_book_repo,
            mock_user_repo,
            mock_book_availability_facade,
            mock_loan_event_dispatcher,
        )

        # Act
        result = await uc.execute(
            user_id=1, book_id=10, max_interest_time=48, requested_loan_time=14
        )

        # Assert
        assert result is False  # queue_length == 0 → waiting, not privileged
        assert fake_uow.committed
        mock_loan_req_repo.save_request.assert_called_once()
        mock_loan_event_dispatcher.notify.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_loan_raises_when_user_not_found(
        self,
        mock_book_repo: AsyncMock,
        mock_user_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_user_repo.get_by_id.return_value = None
        mock_book_repo.get_by_id.return_value = _make_book(10)

        uc = RequestLoan(
            fake_uow,
            mock_loan_req_repo,
            mock_book_repo,
            mock_user_repo,
            mock_book_availability_facade,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(Exception, match="User or Book does not exist"):
            await uc.execute(
                user_id=99, book_id=10, max_interest_time=48, requested_loan_time=14
            )

        mock_loan_req_repo.save_request.assert_not_called()
        mock_loan_event_dispatcher.notify.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_request_loan_raises_when_book_not_found(
        self,
        mock_book_repo: AsyncMock,
        mock_user_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_user_repo.get_by_id.return_value = _make_user(1)
        mock_book_repo.get_by_id.return_value = None

        uc = RequestLoan(
            fake_uow,
            mock_loan_req_repo,
            mock_book_repo,
            mock_user_repo,
            mock_book_availability_facade,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(Exception, match="User or Book does not exist"):
            await uc.execute(
                user_id=1, book_id=99, max_interest_time=48, requested_loan_time=14
            )

        mock_loan_req_repo.save_request.assert_not_called()
        mock_loan_event_dispatcher.notify.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_request_loan_rolls_back_on_save_failure(
        self,
        mock_book_repo: AsyncMock,
        mock_user_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_user_repo.get_by_id.return_value = _make_user(1)
        mock_book_repo.get_by_id.return_value = _make_book(10)
        mock_book_availability_facade.read_availability.return_value = (
            BookAvailability(book_id=BookId(10), no_soft_locked_copies=1, no_hard_locked_copies=1)
        )
        mock_loan_req_repo.save_request.side_effect = RuntimeError("DB error")

        uc = RequestLoan(
            fake_uow,
            mock_loan_req_repo,
            mock_book_repo,
            mock_user_repo,
            mock_book_availability_facade,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await uc.execute(
                user_id=1, book_id=10, max_interest_time=48, requested_loan_time=14
            )

        assert not fake_uow.committed
        mock_loan_event_dispatcher.notify.assert_not_called()
