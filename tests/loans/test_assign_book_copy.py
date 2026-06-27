from datetime import datetime
from unittest.mock import AsyncMock
from books.domain.book import BookTitle, BookISBN, BookDescription, BookEditorial, BookCover, BookLanguage, BookAuthor, BookCategory, BookPageCount

import pytest

from books.domain.book import (
    Book,
    BookId,
)
from books.domain.book_copy import BookCopy, BookCopyId, BookCopyStatus
from loans.application.use_cases.assign_book_copy import AssignBookCopyToLoanRequest
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


def _make_book_copy(physical_id: str, book_id: int) -> BookCopy:
    return BookCopy(
        copy_id=BookCopyId(physical_id),
        book_id=BookId(book_id),
        status=BookCopyStatus.DISPONIBLE,
    )


def _make_loan_request(
    request_id: int, book_id: int, user_id: int = 1
) -> LoanRequest:
    return LoanRequest(
        loan_req_id=LoanRequestId(request_id),
        user_id=UserId(user_id),
        book_id=BookId(book_id),
        book_copy_code=None,
        wait_time=LoanRequestWaitTime(time=48),
        loan_time=LoanRequestTimeRequested(time=14),
        status=LoanRequestStatus.PENDIENTE,
        created_at=datetime.now(),
        modified_at=datetime.now(),
    )


class TestAssignBookCopyToLoanRequest:

    @pytest.mark.asyncio
    async def test_assign_book_copy_successfully(
        self,
        mock_book_repo: AsyncMock,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        book = _make_book(10)
        copy = _make_book_copy("CP-001", 10)
        request = _make_loan_request(1, 10)

        mock_book_repo.get_by_id.return_value = book
        mock_book_copy_repo.get_by_id.return_value = copy
        mock_loan_req_repo.get_by_id.return_value = request

        uc = AssignBookCopyToLoanRequest(
            fake_uow,
            mock_book_copy_repo,
            mock_book_repo,
            mock_loan_req_repo,
            mock_loan_event_dispatcher,
        )

        # Act
        await uc.execute(book_copy="CP-001", book_id=10, request_id=1)

        # Assert
        assert fake_uow.committed
        # Book copy should be reserved (status → PRESTADO)
        assert copy.status == BookCopyStatus.PRESTADO
        # Loan request should be assigned
        assert request.status == LoanRequestStatus.ASIGNADA
        assert request.book_copy_code == copy.copy_id
        # Persistence calls
        mock_book_copy_repo.update_book_copy.assert_called_once_with(copy)
        # Event dispatched
        mock_loan_event_dispatcher.notify.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_when_copy_not_found(
        self,
        mock_book_repo: AsyncMock,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_book_repo.get_by_id.return_value = _make_book(10)
        mock_book_copy_repo.get_by_id.return_value = None
        mock_loan_req_repo.get_by_id.return_value = _make_loan_request(1, 10)

        uc = AssignBookCopyToLoanRequest(
            fake_uow,
            mock_book_copy_repo,
            mock_book_repo,
            mock_loan_req_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Book, book_copy or request does not exist"):
            await uc.execute(book_copy="CP-999", book_id=10, request_id=1)

        mock_book_copy_repo.update_book_copy.assert_not_called()
        mock_loan_event_dispatcher.notify.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_raises_when_book_not_found(
        self,
        mock_book_repo: AsyncMock,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_book_repo.get_by_id.return_value = None
        mock_book_copy_repo.get_by_id.return_value = _make_book_copy("CP-001", 10)
        mock_loan_req_repo.get_by_id.return_value = _make_loan_request(1, 10)

        uc = AssignBookCopyToLoanRequest(
            fake_uow,
            mock_book_copy_repo,
            mock_book_repo,
            mock_loan_req_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Book, book_copy or request does not exist"):
            await uc.execute(book_copy="CP-001", book_id=99, request_id=1)

        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_raises_when_request_not_found(
        self,
        mock_book_repo: AsyncMock,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_book_repo.get_by_id.return_value = _make_book(10)
        mock_book_copy_repo.get_by_id.return_value = _make_book_copy("CP-001", 10)
        mock_loan_req_repo.get_by_id.return_value = None

        uc = AssignBookCopyToLoanRequest(
            fake_uow,
            mock_book_copy_repo,
            mock_book_repo,
            mock_loan_req_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Book, book_copy or request does not exist"):
            await uc.execute(book_copy="CP-001", book_id=10, request_id=99)

        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_rolls_back_on_update_failure(
        self,
        mock_book_repo: AsyncMock,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_book_repo.get_by_id.return_value = _make_book(10)
        mock_book_copy_repo.get_by_id.return_value = _make_book_copy("CP-001", 10)
        mock_loan_req_repo.get_by_id.return_value = _make_loan_request(1, 10)
        mock_book_copy_repo.update_book_copy.side_effect = RuntimeError("DB error")

        uc = AssignBookCopyToLoanRequest(
            fake_uow,
            mock_book_copy_repo,
            mock_book_repo,
            mock_loan_req_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await uc.execute(book_copy="CP-001", book_id=10, request_id=1)

        assert not fake_uow.committed
        mock_loan_event_dispatcher.notify.assert_not_called()
