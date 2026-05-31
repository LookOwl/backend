from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models.solicitud_libro import SolicitudLibro as SolicitudLibroModel
from domain.solicitud_libro import BookRequest
from domain.enums.estado_solicitud import EstadoSolicitud


class SolicitudLibroRepository:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _to_domain(self, model: SolicitudLibroModel) -> BookRequest:
        return BookRequest(
            id=model.id,
            user_id=model.id_usuario,
            copy_code=model.codigo_ejemplar,
            wait_time=model.tiempo_espera,
            status=model.estado,
        )

    def _to_model(self, entity: BookRequest) -> SolicitudLibroModel:
        return SolicitudLibroModel(
            id_usuario=entity.user_id,
            codigo_ejemplar=entity.copy_code,
            tiempo_espera=entity.wait_time,
            estado=entity.status,
        )

    async def create(self, entity: BookRequest) -> BookRequest:
        model = self._to_model(entity)
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, solicitud_id: int) -> Optional[BookRequest]:
        model = await self.db.get(SolicitudLibroModel, solicitud_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def list(
        self,
        user_id: Optional[int] = None,
        status: Optional[EstadoSolicitud] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[BookRequest]:
        stmt = select(SolicitudLibroModel)
        if user_id is not None:
            stmt = stmt.where(SolicitudLibroModel.id_usuario == user_id)
        if status is not None:
            stmt = stmt.where(SolicitudLibroModel.estado == status)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def notify(self, solicitud_id: int) -> Optional[BookRequest]:
        model = await self.db.get(SolicitudLibroModel, solicitud_id)
        if model is None:
            return None
        model.estado = EstadoSolicitud.NOTIFICADA
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def complete(self, solicitud_id: int) -> Optional[BookRequest]:
        model = await self.db.get(SolicitudLibroModel, solicitud_id)
        if model is None:
            return None
        model.estado = EstadoSolicitud.COMPLETADA
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_domain(model)

    async def cancel(self, solicitud_id: int) -> Optional[BookRequest]:
        model = await self.db.get(SolicitudLibroModel, solicitud_id)
        if model is None:
            return None
        model.estado = EstadoSolicitud.CANCELADA
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_domain(model)
