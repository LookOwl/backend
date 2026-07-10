from redis.asyncio import Redis
from redis.commands.core import AsyncScript

#TODO(Falta poner excepciones que sean entendibles para la capa que use esta clase, 
# por el momento solo eleva la excepción inmediatamente)
class RedisController:
    
    _redis : Redis
    AV_SLOTS_PREFIX = "avSlots"
    TOTAL_COPIES_PREFIX = "totCopies"
    DEFAULT_TTL_SECONDS = 3600

    # NOTE: both scripts no-op when the key is absent. Applying a delta to a
    # missing baseline would create a key holding only the delta (e.g. -1),
    # which the reader would then trust instead of rebuilding from the DB. By
    # leaving the key absent, the next read still sees a cache miss and rebuilds
    # from the (already committed) DB state, so no delta is lost.
    INCR_WITH_TTL_SCRIPT = """
        if redis.call('EXISTS', KEYS[1]) == 0 then
            return nil
        end
        local value = redis.call('INCR', KEYS[1])
        redis.call('EXPIRE', KEYS[1], ARGV[1])
        return value
    """

    DECR_WITH_TTL_SCRIPT = """
        if redis.call('EXISTS', KEYS[1]) == 0 then
            return nil
        end
        local value = redis.call('DECR', KEYS[1])
        redis.call('EXPIRE', KEYS[1], ARGV[1])
        return value
    """

    _incr_with_ttl : AsyncScript
    _decr_with_tll : AsyncScript
    _ttl : int  #In seconds


    def __init__(
            self,
            redis : Redis,
            ttl : int = DEFAULT_TTL_SECONDS
        ):
        self._redis = redis
        self._incr_with_tll = redis.register_script(self.INCR_WITH_TTL_SCRIPT)
        self._decr_with_tll = redis.register_script(self.DECR_WITH_TTL_SCRIPT)
        self._ttl = ttl


    async def get_available_slots(self, book_id : int):
        result = await self._redis.get(f"{book_id}:{self.AV_SLOTS_PREFIX}")
        if result is None: raise CacheMissException()       #Recomposition needed
        
        result = int(result)
        return result
    
    async def inc_available_slots(self, book_id : int):
        try:
            await self._incr_with_tll(
                keys=[f"{book_id}:{self.AV_SLOTS_PREFIX}"],
                args=[self._ttl]
            )
            return
        except Exception as e:
            raise e            
    
    async def dec_available_slots(self, book_id : int):
        try:
            await self._decr_with_tll(
                keys=[f"{book_id}:{self.AV_SLOTS_PREFIX}"],
                args=[self._ttl]
            )
        except Exception as e:
            raise e

    async def get_total_copies(self, book_id : int):         
        result = await self._redis.get(f"{book_id}:{self.TOTAL_COPIES_PREFIX}")
        if result is None: raise CacheMissException()       #Recomposition needed

        result = int(result)
        return result
    
    async def inc_total_copies(self, book_id : int):
        try:
            await self._incr_with_tll(
                keys=[f"{book_id}:{self.TOTAL_COPIES_PREFIX}"],
                args=[self._ttl]
            )
        except Exception as e:
            raise e
    
    async def dec_total_copies(self, book_id : int):
        try:
            await self._decr_with_tll(
                keys=[f"{book_id}:{self.TOTAL_COPIES_PREFIX}"],
                args=[self._ttl]
            )
        except Exception as e:
            raise e
    

    async def set_indices(self, book_id:int , total_copies : int, available_slots :int):
        try:
            await self._redis.set(f"{book_id}:{self.AV_SLOTS_PREFIX}",available_slots, ex=self._ttl)
            await self._redis.set(f"{book_id}:{self.TOTAL_COPIES_PREFIX}",total_copies,ex=self._ttl)
        except Exception as e:
            raise e
        

class CacheMissException(Exception): pass