from fastapi import Request, Depends
from old.infrastructure.database.connection import async_session_factory
from redis.asyncio import Redis
from old.infrastructure.redis.lock import RedisLockManager
from old.infrastructure.redis.redis_controller import RedisController

async def async_get_db_session():
    async with async_session_factory() as session:
        yield session


def get_redis(request : Request):
    return request.app.state.redis

def get_redis_controller(
        redis : Redis = Depends(get_redis)
    ):
    return RedisController(redis)

def get_redis_lock_manager(
    redis : Redis = Depends(get_redis)
):
    return RedisLockManager(
        redis,
        10
    )