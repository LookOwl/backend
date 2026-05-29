from repositories.solicitud_libro_repository import SolicitudLibroRepository
from domain.solicitud_libro import BookRequest
from redis import Redis

lua_safe_decrement_script = """
local current = tonumber(redis.call('get', KEYS[1]))
if current and current > 0 then
    return redis.call('decr', KEYS[1])
else
    return current or 0
end
"""

class QueueService:

    redis: Redis
    request_repo: SolicitudLibroRepository
    def __init__(
        self,
        instance: Redis,
        request_repository: SolicitudLibroRepository
    ):
        self.redis = instance
        self.request_repo = request_repository

    '''Revisa si la cola privilegiada de un libro está vacía
    Requiere: El id del perfil del libro
    Devuelve: Valor booleano `true`|`false` en caso si | no esté vacía '''
    async def isPriviledgedFull(self,book_id) -> bool:
        soft_lock_key : str = f"{book_id}_sl"
        try:
            value = int(self.redis.get(soft_lock_key))
        except ValueError:
            raise FatalQueueException
        return value == 0

    '''Inserta un pedido de préstamo en la cola del libro correspondiente
    Requiere: Id del libro, objeto de pedido
    Devuelve: Nada'''
    async def insertIntoQueue(self,book_id : int, req : BookRequest ):
        try:
            #Primero, intentar insertar el préstamo en la cola
            created_request = self.request_repo.create(req)
            #Luego, aumentar el soft_lock
            soft_lock_key : str = f""
        except Exception as e:
            raise FatalQueueException


class FatalQueueException(Exception):pass