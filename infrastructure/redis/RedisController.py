from redis import Redis


#TODO(Falta poner excepciones que sean entendibles para la capa que use esta clase, 
# por el momento solo eleva la excepción inmediatamente)
class RedisController:
    
    _redis : Redis

    AV_SLOTS_PREFIX = "av_sl"
    TOTAL_COPIES_PREFIX = "tot_cps"

    def __init__(
            self,
            redis : Redis
        ):
        self._redis = redis

    async def get_available_slots(self, book_id : int):
        try:
            result = await self._redis.get(f"{book_id}_{self.AV_SLOTS_PREFIX}")
            result = int(result)
            return result
        except ValueError as e:
            if result is None: return 0
            else: raise e
        except Exception as e:
            raise e
        
    async def inc_available_slots(self, book_id : int):
        try:
            return await self._redis.incr(f"{book_id}_{self.AV_SLOTS_PREFIX}")
        except Exception as e:
            raise e            
    
    async def dec_available_slots(self, book_id : int):
        try:
            return await self._redis.decr(f"{book_id}_{self.AV_SLOTS_PREFIX}")
        except Exception as e:
            raise e

    async def get_total_copies(self, book_id : int):
        try:
            result = await self._redis.get(f"{book_id}_{self.TOTAL_COPIES_PREFIX}")
            result = int(result)
            return result
        except ValueError as e:
            if result is None: return 0
            else: raise e
        except Exception as e:
            raise e
        
    
    async def inc_total_copies(self, book_id : int):
        try:
            return await self._redis.incr(f"{book_id}_{self.TOTAL_COPIES_PREFIX}")
        except Exception as e:
            raise e
    
    async def dec_total_copies(self, book_id : int):
        try:
            return await self._redis.decr(f"{book_id}_{self.TOTAL_COPIES_PREFIX}")
        except Exception as e:
            raise e
    

    async def init_index(self, book_id:int , total_copies : int, available_slots :int):
        try:
            await self._redis.set(f"{book_id}_{self.AV_SLOTS_PREFIX}",available_slots)
            await self._redis.set(f"{book_id}_{self.TOTAL_COPIES_PREFIX}",total_copies)
        except Exception as e:
            raise e