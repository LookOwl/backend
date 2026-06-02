from infrastructure.database.connection import async_session_factory
from infrastructure.database.models.solicitud_libro import SolicitudLibro, EstadoSolicitud
from infrastructure.database.models.prestamo import Prestamo, EstadoPrestamo
from infrastructure.database.models.libro import Libro
from infrastructure.database.models.ejemplar import Ejemplar, EstadoEjemplar
from infrastructure.redis.redis_controller import RedisController
from sqlalchemy import select, func, or_, and_
from redis.asyncio import Redis

async def seed(redis : Redis):
    async with async_session_factory() as session:
        redis_controller = RedisController(redis)
        query = select(Libro.id)
        #Obetener todos los ids de los libros en la base de datos
        book_ids = await session.execute(query)
        #Para cada uno de ellos
        for book_id in book_ids.scalars():
            
            #Primero, calcular cuantas copias físicas disponibles existen
            available_copies_id = (await session.execute(
                select(
                    func.count(Ejemplar.id)
                ).where(
                    Ejemplar.libro_id == book_id,
                    Ejemplar.estado == EstadoEjemplar.DISPONIBLE
                )
            )).scalars().all()

            #Número de solicitudes en la cola
            n_total_requests = (await session.execute(
                select(
                    func.count(SolicitudLibro.id)
                ).where(
                    SolicitudLibro.id_libro == book_id
                ).where(
                    SolicitudLibro.estado == EstadoSolicitud.PENDIENTE
                )
            )).scalar()
            
            total_copies = available_copies_id
            available_slots = total_copies - n_total_requests

            redis_controller.init_index(book_id,total_copies,available_slots)


            
                