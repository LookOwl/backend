from redis import Redis

class RedisController:
    
    redis : Redis

    def __init__(
            self,
            redis : Redis
        ):
        self.redis = redis

    def get_available_slots(self, book_id : int):
        pass

    def inc_available_slots(self, book_id : int):
        pass    
    
    def get_total_copies(self, book_id : int):
        pass
    
    def inc_total_copies(self, book_id : int):
        pass
    