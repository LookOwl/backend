from infrastructure.database.connection import async_session_factory
from infrastructure.database.models.solicitud_libro import SolicitudLibro
from infrastructure.database.models.libro import Libro
from infrastructure.database.models.ejemplar import Ejemplar 
from sqlalchemy import select, func

async def seed():
    async with async_session_factory() as session:
        query = select(Libro.id)
        #Obetener todos los ids de los libros en la base de datos
        book_ids = await session.execute(query)
        #Para cada uno de ellos
        for id in book_ids.scalars():
            #Primero, calcular cuantas copias físicas existen
            n_copies = (await session.execute(select(
                func.count(Ejemplar.id)
            ).where(Ejemplar.libro_id == id))).scalar()
            #Número de solicitudes en la cola
            n_requests = (await session.execute(
                select(
                    func.count(SolicitudLibro.id)
                ).where(
                    SolicitudLibro.
                )
            )) 
            
                