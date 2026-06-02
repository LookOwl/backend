from uow.ApplicationUOW import AppUnitOfWork
from infrastructure.redis.redis_controller import RedisController
from infrastructure.redis.lock import RedisLockManager
from domain.solicitud_libro import BookRequest, EstadoSolicitud
from domain.book_copy import BookCopy, EstadoEjemplar
from domain.user import User
class BorrowingOrchestrator:

    def __init__(
            self,
            uow : AppUnitOfWork,
            lock_manager : RedisLockManager,
            redis_controller: RedisController    
        ):
        self._uow = uow
        self._lock_manager = lock_manager
        self._redis_controller = redis_controller

    async def submit_loan_request(self,book_id : int, user: User, req : BookRequest ):
        #Caso añadir un request a la cola. Lo primero es ver siquiera si el usuario puede añadir algo a la cola
        
        async with self._uow as uow:
            n_requests_in_queue = await uow.solicitud_libro_repo.list(user_id=user.uid,limit=3, status=EstadoSolicitud.PENDIENTE) 
        #Por el momento la única regla TODO(Verificar si añadir mas reglas)
        if(n_requests_in_queue == 3 ):
            raise ForbiddenOperationException("Usuario tiene más de 3 solicitudes en cola")
        
        # Verificar si la ventana privilegiada está llena
        #Necesitamos bloquear el acceso a tales índices en redis
        async with self._lock_manager.acquire(str(book_id)) as lock:
            available_slots = self._redis_controller.get_available_slots(book_id)
            if(available_slots <= 0):
                #Si la cola está llena, avisar al usuario que está llena la cola
                #TODO( Añadir un pedido "fastasma" con un corto TTL que permita al usuario adquirir el espacio)
                raise FullPriviledgeQueueException("Cola llena")
            else:
                async with self._uow as uow:
                    uow.solicitud_libro_repo.create(req)
                    self._redis_controller.dec_available_slots(book_id)
    
    async def cancel_request_in_queue(self, book_id: int, req_id : int ):
        async with self._uow as uow:
            #Verificar que existe en la cola
            request = await uow.solicitud_libro_repo.get_by_id(req_id)
            if(request is None ): raise NullObjectException(f"Request {req_id} to delete is null")
            
            #Si existe, entonces procedamos a borrarlo: Bloqueemos el índice de redis
            async with self._lock_manager.acquire(book_id):
                uow.solicitud_libro_repo.cancel(book_id)
                self._redis_controller.inc_available_slots(book_id)
    
    async def assign_book_copy_to_request(self, book_id: int, req_id: int, book_copy_id : int):
        #Primero un lock sobre la base de datos: no queremos asignar un libro que quizás ya esté tomado
        async with self._uow as uow:
            #Checks sobre la copia física
            book_copy_status = await uow.book_copy_repo.get_status(book_copy_id)
            if( book_copy_status is None or book_copy_status != EstadoEjemplar.DISPONIBLE ):
                raise ForbiddenOperationException(f"El libro {book_copy_id} no está disponible")
            #Checks sobre el estado del request en sí (no queremos que un request cancelado tenga un libro asignado)
            request = await uow.solicitud_libro_repo.get_by_id(req_id)
            if(request.status != EstadoSolicitud.PENDIENTE): raise ForbiddenOperationException("La solicitud no es válida para esta operación")
            #En caso está disponible, entonces asignémoslo
            #Eso implica: reducir un índice de redis (el de total_copies) 
            # y modificar el estado del pedido en la base de datos

            async with self._lock_manager.acquire(str(book_id)):
                uow.solicitud_libro_repo.notify() #Pendiente, el repositorio es el correcto?

class NullObjectException(Exception) : pass
class FullPriviledgeQueueException(Exception) : pass
class ForbiddenOperationException(Exception) : pass