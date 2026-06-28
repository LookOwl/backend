import asyncio
from redis.asyncio import Redis
from uuid import uuid4


class RedisLock:

    RELEASE_SCRIPT = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """

    _lock_id : str
    _lock_key : str

    def __init__(
            self,
            redis: Redis,
            key: str,   #BookId
            ttl: int,
            wait: bool = False,
            retry_delay: float = 0.1,
            timeout : float = 5.0
        ):
        self._redis = redis 
        self._lock_key =  f"lock:{key}"
        self._lock_id = str(uuid4())
        self._ttl = ttl
        self._wait = wait
        self._retry_delay = retry_delay
        self._timeout = timeout 
        


    async def __aenter__(self):
        if self._wait:
            await self._acquire_with_retry()
        else:
            await self._acquire_or_raise()
        return self
        

    async def __aexit__(self, exc_type, exc, tb): #type: ignore
        await self._redis.eval(
            self.RELEASE_SCRIPT,1,self._lock_key, self._lock_id
        )
        return False #Propagate errors

    async def _acquire_with_retry(self):
        elapsed = 0.0
        while elapsed < self._timeout:
            acquired = await self._redis.set(
                self._lock_key,
                self._lock_id,
                nx=True,
                ex=self._ttl
            )
            if acquired:
                return
            await asyncio.sleep(self._retry_delay)
            elapsed += self._retry_delay
        raise LockTimeoutException(f"Cannot acquired lock in the specified time")
    
    async def _acquire_or_raise(self):
        acquired = await self._redis.set(
            self._lock_key, self._lock_id, nx= True, ex=self._ttl
        )
        if not acquired:
            raise LockNotAdquiredException("Could not acquire lock")



class RedisLockManager:

    _redis : Redis
    _ttl : int
    def __init__(
            self, 
            redis : Redis,
            ttl : int = 10,
        ):
        self._redis = redis
        self._ttl = ttl

    
    def acquire(self, book_id:str, ttl:int | None = None,wait : bool = True, timeout : float = 5.0):
        return RedisLock(
            redis=self._redis,
            key=book_id,
            ttl=ttl or self._ttl,
            wait=wait,
            timeout=timeout
        )
        

class LockNotAdquiredException(Exception): pass
class LockTimeoutException(Exception) : pass