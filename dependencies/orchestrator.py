from fastapi import Depends
from orchestrator.borrowing_orchestrator import BorrowingOrchestrator
from dependencies.infrastructure import get_redis_controller, get_redis_lock_manager
from dependencies.uow import get_unit_of_work

def get_borrowing_orchestrator(
        uow = Depends(get_unit_of_work),
        redis_lock_manager = Depends(get_redis_lock_manager),
        redis_controller = Depends(get_redis_controller)
):
    return BorrowingOrchestrator(
        uow=uow,
        lock_manager=redis_lock_manager,
        redis_controller=redis_controller
    )