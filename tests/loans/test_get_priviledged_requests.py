from datetime import datetime, timezone
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
from loans.application.use_cases.get_priviledged_requests import GetPriviledgedRequests
from loans.domain.loan_request import (
    LoanRequest,
    LoanRequestId,
    LoanRequestStatus,
    LoanRequestTimeRequested,
    LoanRequestWaitTime,
)
from users.domain.user_id import UserId


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


def _make_loan_request(request_id: int, book_id: int, user_id: int = 1) -> LoanRequest:
    return LoanRequest(
        loan_req_id=LoanRequestId(request_id),
        user_id=UserId(user_id),
        book_id=BookId(book_id),
        book_copy_code=None,
        wait_time=LoanRequestWaitTime(time=48),
        loan_time=LoanRequestTimeRequested(time=14),
        status=LoanRequestStatus.PENDIENTE,
        created_at=datetime.now(timezone.utc),
        modified_at=datetime.now(timezone.utc),
    )


class TestGetPriviledgedRequests:

    @pytest.mark.asyncio
    async def test_returns_privileged_requests(
        self,
        mock_book_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        book = _make_book(10)
        mock_book_repo.get_by_id.return_value = book
        # 2 hard-locked copies → 2 privileged slots
        mock_book_availability_facade.read_availability.return_value = (
            BookAvailability(book_id=book.book_id, no_soft_locked_copies=5, no_hard_locked_copies=2)
        )
        expected_requests = [
            _make_loan_request(1, 10),
            _make_loan_request(2, 10, user_id=3),
        ]
        mock_loan_req_repo.get_n_first_pending_by_book_id.return_value = expected_requests

        uc = GetPriviledgedRequests(
            fake_uow, mock_book_repo, mock_loan_req_repo, mock_book_availability_facade
        )

        # Act
        result = await uc.execute(book_id=10)

        # Assert
        assert len(result) == 2
        assert result == expected_requests
        assert fake_uow.committed
        mock_loan_req_repo.get_n_first_pending_by_book_id.assert_called_once_with(
            book.book_id, 2  # limit = no_hard_locked_copies
        )

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_hard_locked_copies(
        self,
        mock_book_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        book = _make_book(10)
        mock_book_repo.get_by_id.return_value = book
        mock_book_availability_facade.read_availability.return_value = (
            BookAvailability(book_id=book.book_id, no_soft_locked_copies=5, no_hard_locked_copies=0)
        )
        mock_loan_req_repo.get_n_first_pending_by_book_id.return_value = []

        uc = GetPriviledgedRequests(
            fake_uow, mock_book_repo, mock_loan_req_repo, mock_book_availability_facade
        )

        # Act
        result = await uc.execute(book_id=10)

        # Assert
        assert result == []
        assert fake_uow.committed
        mock_loan_req_repo.get_n_first_pending_by_book_id.assert_called_once_with(
            book.book_id, 0
        )

    @pytest.mark.asyncio
    async def test_raises_when_book_not_found(
        self,
        mock_book_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_book_repo.get_by_id.return_value = None

        uc = GetPriviledgedRequests(
            fake_uow, mock_book_repo, mock_loan_req_repo, mock_book_availability_facade
        )

        # Act & Assert
        with pytest.raises(Exception, match="No book found"):
            await uc.execute(book_id=99)

        mock_loan_req_repo.get_n_first_pending_by_book_id.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_rolls_back_on_availability_error(
        self,
        mock_book_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_book_availability_facade: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        book = _make_book(10)
        mock_book_repo.get_by_id.return_value = book
        mock_book_availability_facade.read_availability.side_effect = RuntimeError("Redis down")

        uc = GetPriviledgedRequests(
            fake_uow, mock_book_repo, mock_loan_req_repo, mock_book_availability_facade
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Redis down"):
            await uc.execute(book_id=10)

        assert not fake_uow.committed
