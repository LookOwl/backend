from redis.asyncio import Redis


#TODO(Falta poner excepciones que sean entendibles para la capa que use esta clase, 
# por el momento solo eleva la excepción inmediatamente)
class RedisController:
    
    _redis : Redis

    AV_SLOTS_PREFIX = "avSlots"
    TOTAL_COPIES_PREFIX = "totCopies"
    VALID_CACHE_PREFIX = "valid"

    def __init__(
            self,
            redis : Redis
        ):
        self._redis = redis

    async def get_available_slots(self, book_id : int):
        
        is_valid = await self._redis.get(f"{book_id}:{self.VALID_CACHE_PREFIX}")
        if(not is_valid): raise CacheMissException()    #Recomposition triggered
        is_valid = bool(is_valid)

        if(not is_valid): raise CacheMissException()    #Recomposition triggered            

        result = await self._redis.get(f"{book_id}:{self.AV_SLOTS_PREFIX}")
        if not result: raise CacheMissException()       #Recomposition needed

        result = int(result)
        return result
    
    async def inc_available_slots(self, book_id : int):
        try:
            return await self._redis.incr(f"{book_id}:{self.AV_SLOTS_PREFIX}")
        except Exception as e:
            raise e            
    
    async def dec_available_slots(self, book_id : int):
        try:
            return await self._redis.decr(f"{book_id}:{self.AV_SLOTS_PREFIX}")
        except Exception as e:
            raise e

    async def get_total_copies(self, book_id : int):
        is_valid = await self._redis.get(f"{book_id}:{self.VALID_CACHE_PREFIX}")
        if(not is_valid): raise CacheMissException()    #Recomposition triggered
        is_valid = bool(is_valid)

        if(not is_valid): raise CacheMissException()    #Recomposition triggered            

        result = await self._redis.get(f"{book_id}:{self.TOTAL_COPIES_PREFIX}")
        if not result: raise CacheMissException()       #Recomposition needed

        result = int(result)
        return result
    
    async def inc_total_copies(self, book_id : int):
        try:
            return await self._redis.incr(f"{book_id}:{self.TOTAL_COPIES_PREFIX}")
        except Exception as e:
            raise e
    
    async def dec_total_copies(self, book_id : int):
        try:
            return await self._redis.decr(f"{book_id}:{self.TOTAL_COPIES_PREFIX}")
        except Exception as e:
            raise e
    

    async def set_indices(self, book_id:int , total_copies : int, available_slots :int):
        try:
            await self._redis.set(f"{book_id}:{self.AV_SLOTS_PREFIX}",available_slots)
            await self._redis.set(f"{book_id}:{self.TOTAL_COPIES_PREFIX}",total_copies)
        except Exception as e:
            raise e
        

class CacheMissException(Exception): pass