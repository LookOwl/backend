from unittest.mock import AsyncMock, MagicMock
import pytest

from books.application.book_availability_facade import BookAvailabilityFacade
from books.domain.book_copy_repository import BookCopyRepository
from books.domain.book_repository import BookRepository
from loans.application.loan_request_dispatcher import LoanRequestEventDispatcher
from loans.domain.loan_request_repo import LoanRequestRepository
from users.domain.user_repository import UserRepository
from shared.application.unit_of_work import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    """A fake UnitOfWork that tracks begin/commit/rollback calls without a real DB."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.began = False

    async def begin(self) -> None:
        self.began = True

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def fake_uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def mock_book_repo() -> AsyncMock:
    """Returns an AsyncMock spec'd to BookRepository."""
    return AsyncMock(spec=BookRepository)


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Returns an AsyncMock spec'd to UserRepository."""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_loan_req_repo() -> AsyncMock:
    """Returns an AsyncMock spec'd to LoanRequestRepository."""
    return AsyncMock(spec=LoanRequestRepository)


@pytest.fixture
def mock_book_availability_facade() -> AsyncMock:
    """Returns an AsyncMock spec'd to BookAvailabilityFacade."""
    return AsyncMock(spec=BookAvailabilityFacade)


@pytest.fixture
def mock_loan_event_dispatcher() -> AsyncMock:
    """Returns an AsyncMock spec'd to LoanRequestEventDispatcher."""
    return AsyncMock(spec=LoanRequestEventDispatcher)


@pytest.fixture
def mock_book_copy_repo() -> AsyncMock:
    """Returns an AsyncMock spec'd to BookCopyRepository."""
    return AsyncMock(spec=BookCopyRepository)
