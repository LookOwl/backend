

from fastapi import Depends, Request
from redis.asyncio import Redis

from shared.infrastructure.cache.lock import RedisLockManager
from shared.infrastructure.cache.redis_controller import RedisController


async def get_redis_session(
    request : Request
):
    assert isinstance(request.app.state.redis, Redis)
    return request.app.state.redis


async def get_redis_controller(
    redis : Redis = Depends(get_redis_session)       
):
    return RedisController(
        redis
    )

async def get_redis_lock_manager(
    redis : Redis = Depends(get_redis_session)
):
    return RedisLockManager(
        redis
    )

