from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from books.domain.book import (
    BookId,
)
from books.domain.book_copy import (
    BookCopy,
    BookCopyId,
    BookCopyStatus,
    PhysicalBookCopyId,
)
from loans.application.use_cases.assign_copy_to_request import (
    AssignBookCopyToLoanRequestUseCase,
    CopyNoAvailableException,
    CopyNoExistsException,
    InvalidLoanRequestException,
)
from loans.domain.loan_request import (
    LoanRequest,
    LoanRequestId,
    LoanRequestStatus,
    LoanRequestTimeRequested,
    LoanRequestWaitTime,
)
from users.domain.user_id import UserId


def _make_book_copy(
    internal_id: int, physical_code: str, book_id: int
) -> BookCopy:
    return BookCopy(
        id=BookCopyId(internal_id),
        physical_copy_id=PhysicalBookCopyId(physical_code),
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
        created_at=datetime.now(timezone.utc),
        modified_at=datetime.now(timezone.utc),
    )


class TestAssignBookCopyToLoanRequestUseCase:

    @pytest.mark.asyncio
    async def test_assign_book_copy_successfully(
        self,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        copy = _make_book_copy(internal_id=100, physical_code="CP-001", book_id=10)
        request = _make_loan_request(1, 10)

        mock_book_copy_repo.get_by_physical_id.return_value = copy
        mock_loan_req_repo.get_by_id.return_value = request

        uc = AssignBookCopyToLoanRequestUseCase(
            fake_uow,
            mock_loan_req_repo,
            mock_book_copy_repo,
            mock_loan_event_dispatcher,
        )

        # Act
        await uc.execute(req_id=1, book_copy_code="CP-001")

        # Assert
        assert fake_uow.committed
        # Book copy should be reserved (status → PRESTADO)
        assert copy.status == BookCopyStatus.PRESTADO
        # Loan request should be assigned
        assert request.status == LoanRequestStatus.ASIGNADA
        assert request.book_copy_code == copy.id
        # Persistence calls
        mock_book_copy_repo.update_book_copy.assert_called_once_with(copy)
        mock_loan_req_repo.update_loan_request.assert_called_once_with(request)
        # Event dispatched
        mock_loan_event_dispatcher.notify.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_when_copy_not_found(
        self,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_book_copy_repo.get_by_physical_id.return_value = None
        mock_loan_req_repo.get_by_id.return_value = _make_loan_request(1, 10)

        uc = AssignBookCopyToLoanRequestUseCase(
            fake_uow,
            mock_loan_req_repo,
            mock_book_copy_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(CopyNoExistsException):
            await uc.execute(req_id=1, book_copy_code="CP-999")

        mock_book_copy_repo.update_book_copy.assert_not_called()
        mock_loan_event_dispatcher.notify.assert_not_called()
        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_raises_when_copy_not_available(
        self,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        already_reserved = BookCopy(
            id=BookCopyId(100),
            physical_copy_id=PhysicalBookCopyId("CP-002"),
            book_id=BookId(10),
            status=BookCopyStatus.PRESTADO,
        )
        mock_book_copy_repo.get_by_physical_id.return_value = already_reserved
        mock_loan_req_repo.get_by_id.return_value = _make_loan_request(1, 10)

        uc = AssignBookCopyToLoanRequestUseCase(
            fake_uow,
            mock_loan_req_repo,
            mock_book_copy_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(CopyNoAvailableException):
            await uc.execute(req_id=1, book_copy_code="CP-002")

        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_raises_when_request_not_found(
        self,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        mock_book_copy_repo.get_by_physical_id.return_value = _make_book_copy(
            internal_id=100, physical_code="CP-001", book_id=10
        )
        mock_loan_req_repo.get_by_id.return_value = None

        uc = AssignBookCopyToLoanRequestUseCase(
            fake_uow,
            mock_loan_req_repo,
            mock_book_copy_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(InvalidLoanRequestException):
            await uc.execute(req_id=99, book_copy_code="CP-001")

        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_raises_when_request_not_pending(
        self,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        already_assigned = _make_loan_request(1, 10)
        already_assigned.status = LoanRequestStatus.ASIGNADA

        mock_book_copy_repo.get_by_physical_id.return_value = _make_book_copy(
            internal_id=100, physical_code="CP-001", book_id=10
        )
        mock_loan_req_repo.get_by_id.return_value = already_assigned

        uc = AssignBookCopyToLoanRequestUseCase(
            fake_uow,
            mock_loan_req_repo,
            mock_book_copy_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(InvalidLoanRequestException):
            await uc.execute(req_id=1, book_copy_code="CP-001")

        assert not fake_uow.committed

    @pytest.mark.asyncio
    async def test_rolls_back_on_update_failure(
        self,
        mock_book_copy_repo: AsyncMock,
        mock_loan_req_repo: AsyncMock,
        mock_loan_event_dispatcher: AsyncMock,
        fake_uow,
    ) -> None:
        # Arrange
        copy = _make_book_copy(internal_id=100, physical_code="CP-001", book_id=10)
        mock_book_copy_repo.get_by_physical_id.return_value = copy
        mock_loan_req_repo.get_by_id.return_value = _make_loan_request(1, 10)
        mock_book_copy_repo.update_book_copy.side_effect = RuntimeError("DB error")

        uc = AssignBookCopyToLoanRequestUseCase(
            fake_uow,
            mock_loan_req_repo,
            mock_book_copy_repo,
            mock_loan_event_dispatcher,
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="DB error"):
            await uc.execute(req_id=1, book_copy_code="CP-001")

        assert not fake_uow.committed
        mock_loan_event_dispatcher.notify.assert_not_called()
