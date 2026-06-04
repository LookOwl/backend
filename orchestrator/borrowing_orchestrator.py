from datetime import date, datetime, timedelta

from uow.ApplicationUOW import AppUnitOfWork
from infrastructure.redis.redis_controller import RedisController
from infrastructure.redis.lock import RedisLockManager
from domain.solicitud_libro import BookRequest, EstadoSolicitud
from domain.book_copy import BookCopy, EstadoEjemplar
from domain.loan import Loan, EstadoPrestamo
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

    async def submit_loan_request(self, user: User, req : BookRequest ):
        #Caso añadir un request a la cola. Lo primero es ver siquiera si el usuario puede añadir algo a la cola
        #Reglas TODO(Incluir sanciones)        
        if(req.loan_time < 1 or req.loan_time > 13):
            raise ForbiddenOperationException("El tiempo de préstamo solicitado no es válido")
        async with self._uow as uow:
            n_requests_in_queue = await uow.solicitud_libro_repo.list(user_id=user.uid,limit=3, status=EstadoSolicitud.PENDIENTE) 
            if(n_requests_in_queue >= 3 ):
                raise ForbiddenOperationException("Usuario tiene 3 o más solicitudes en cola")
        
        
        # Verificar si la ventana privilegiada está llena
        #Necesitamos bloquear el acceso a tales índices en redis
        async with self._lock_manager.acquire(str(req.book_id)) as lock:
            available_slots = self._redis_controller.get_available_slots(req.book_id)
            if(available_slots <= 0):
                #Si la cola está llena, avisar al usuario que está llena la cola
                #TODO( Añadir un pedido "fastasma" con un corto TTL que permita al usuario adquirir el espacio)
                raise FullPriviledgeQueueException("Cola llena")
            else:
                async with self._uow as uow:
                    uow.solicitud_libro_repo.create(req)
                    self._redis_controller.dec_available_slots(req.book_id)
    
    async def cancel_request_in_queue(self, req_id : int ):
        async with self._uow as uow:
            #Verificar que existe en la cola
            request = await uow.solicitud_libro_repo.get_by_id(req_id)
            if(request is None ): raise NullObjectException(f"Request {req_id} to delete is null")
            
            #Si existe, entonces procedamos a borrarlo: Bloqueemos el índice de redis
            async with self._lock_manager.acquire(str(request.book_id)):
                uow.solicitud_libro_repo.cancel(str(request.book_id))
                self._redis_controller.inc_available_slots(str(request.book_id))
    
    async def cancel_request_notified(self, req_id : int ):
        async with self._uow as uow:
            #Verificar la existencia y su estado
            request = await uow.solicitud_libro_repo.get_by_id(req_id)
            if(request is None): 
                raise NullObjectException(f"Solicitud {req_id} no existe o no está notificada")
            if (request.status != EstadoSolicitud.NOTIFICADA):
                raise ForbiddenOperationException(f"Solicitud {req_id} no está notificada, por lo que no se puede cancelar de esta forma")
            #Si existe, entonces cancelemoslo:
            async with self._lock_manager.acquire(str(request.book_id)):
                uow.solicitud_libro_repo.cancel(str(request.book_id))
                #Al cancelar una solicitud notificada, el libro que se le asignó vuelve a estar disponible, así que incrementamos el total de copias disponibles en redis
                self._redis_controller.inc_total_copies(str(request.book_id))
                self._redis_controller.inc_available_slots(str(request.book_id))

    async def get_priviledged_queue(self, book_id : int):
        async with self._uow as uow:
            async with self._lock_manager.acquire(str(book_id)):
                total_copies = self._redis_controller.get_total_copies(str(book_id))
                requests = await uow.solicitud_libro_repo.list(
                    book_id=book_id,
                    status=EstadoSolicitud.PENDIENTE, 
                    limit=total_copies,
                    offset=0
                )
                return requests


    async def assign_book_copy_to_request(self, req_id: int, book_copy_id : str):
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

            #TODO(PENDIENTE)
            async with self._lock_manager.acquire(str(request.book_id)):
                #Asignación
                await uow.solicitud_libro_repo.notify(req_id,book_copy_id)
                #Decremento del total de copias disponibles en redis
                await self._redis_controller.dec_total_copies(str(request.book_id))
                await self._redis_controller.dec_available_slots(str(request.book_id))

    #Caso de uso: El usuario va a la biblioteca a retirar el libro, entonces el bibliotecario inicia el préstamo        
    async def start_loan(self, req_id : int):
        async with self._uow as uow:
            waiting_loan = await uow.solicitud_libro_repo.get_by_id(req_id)
            #Para empezar un préstamo, el estado del pedido debe ser NOTIFICADA
            if waiting_loan.status != EstadoSolicitud.NOTIFICADA:
                raise ForbiddenOperationException("El préstamo no está pendiente de inicio")
            #Si lo está, entonces creemos la entidad de préstamo
            loan = Loan(
                id = None,
                user_id = waiting_loan.user_id,
                copy_code = waiting_loan.copy_code,
                solicitud_id=req_id,
                approval_date= datetime.now(),
                due_date= datetime.now() + timedelta(days = waiting_loan.loan_time),
                return_date= None,
                status= EstadoPrestamo.ACTIVO
            )
            #Guardemos el préstamo en la base de datos
            uow.loan_repo.create(loan)
            #Se supone que cuando se asignó el libro a la solicitud,
            #  ya disminuyó el índice en redis. Así que no hay nada que tocar en redis

    #Caso de uso: Usuario entrega el libro prestado
    async def end_loan(self,loan_id:int):
        async with self._uow as uow:
            loan = await uow.loan_repo.get_by_id(loan_id)
            if(loan is None or loan.status != EstadoPrestamo.ACTIVO):
                raise ForbiddenOperationException("El préstamo no es válido para esta operación")
            
            #Si el préstamo es válido, entonces se termina
            # y tambien aumenta en redis el número de copias disponibles del libro
            # Para ello, necesitamos el id del perfil de la copia del libro
            copy = await uow.book_copy_repo.get_by_id(loan.copy_code)
            async with self._lock_manager.acquire(str(copy.libro_id)):
                uow.loan_repo.close(loan_id,datetime.now())
                uow.book_copy_repo.mark_available(loan.copy_code)
                #Al terminar un préstamo, el libro vuelve a estar disponible, así que incrementamos el total de copias disponibles en redis
                self._redis_controller.inc_total_copies(copy.libro_id)
                self._redis_controller.inc_available_slots(copy.libro_id)
                

class NullObjectException(Exception) : pass
class FullPriviledgeQueueException(Exception) : pass
class ForbiddenOperationException(Exception) : pass