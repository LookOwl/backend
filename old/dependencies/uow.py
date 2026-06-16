from fastapi import Depends
from old.dependencies.infrastructure import async_get_db_session
from old.uow.ApplicationUOW import AppUnitOfWork

def get_unit_of_work(
    db = Depends(async_get_db_session)
):
    return AppUnitOfWork(db)