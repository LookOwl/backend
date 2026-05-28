from typing import Optional, Sequence
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from db.models.prestamo import Prestamo
from domain.loan import Loan
from domain.enums.estado_prestamos import EstadoPrestamo

class LoanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_domain(self, prestamo_model: Prestamo) -> Loan:
        return Loan(
            id=prestamo_model.id,
            user_id=prestamo_model.id_usuario_asociado,
            copy_code=prestamo_model.codigo_ejemplar,
            loan_days=prestamo_model.dias_prestamo,
            approval_date=prestamo_model.fecha_aprobacion,
            due_date=prestamo_model.fecha_vencimiento,
            return_date=prestamo_model.fecha_regreso,
            status=prestamo_model.estado,
        )

    def _to_model(self, loan_entity: Loan) -> Prestamo:
        return Prestamo(
            id_usuario_asociado=loan_entity.user_id,
            codigo_ejemplar=loan_entity.copy_code,
            dias_prestamo=loan_entity.loan_days,
            fecha_regreso=loan_entity.return_date,
            estado=loan_entity.status,
        )

    def create(self, loan_entity: Loan) -> Loan:
        prestamo_model = self._to_model(loan_entity)
        self.db.add(prestamo_model)
        self.db.commit()
        self.db.refresh(prestamo_model)
        return self._to_domain(prestamo_model)

    def get_by_id(self, loan_id: int) -> Optional[Loan]:
        prestamo_model = self.db.get(Prestamo, loan_id)
        if prestamo_model is None:
            return None
        return self._to_domain(prestamo_model)

    def list(
        self,
        user_id: Optional[int] = None,
        copy_code: Optional[str] = None,
        status: Optional[EstadoPrestamo] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Loan]:
        stmt = select(Prestamo)
        if user_id is not None:
            stmt = stmt.where(Prestamo.id_usuario_asociado == user_id)
        if copy_code is not None:
            stmt = stmt.where(Prestamo.codigo_ejemplar == copy_code)
        if status is not None:
            stmt = stmt.where(Prestamo.estado == status)
        stmt = stmt.limit(limit).offset(offset)
        prestamos = self.db.execute(stmt).scalars().all()
        return [self._to_domain(prestamo) for prestamo in prestamos]

    def count_active_by_user(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Prestamo)
            .where(
                Prestamo.id_usuario_asociado == user_id,
                Prestamo.estado.in_([EstadoPrestamo.ACTIVO, EstadoPrestamo.PENDIENTE, EstadoPrestamo.VENCIDO]),
            )
        )
        return self.db.execute(stmt).scalar_one()

    def close(self, loan_id: int, return_date: date) -> Optional[Loan]:
        prestamo_model = self.db.get(Prestamo, loan_id)
        if prestamo_model is None:
            return None

        prestamo_model.estado = EstadoPrestamo.CONCLUIDO
        prestamo_model.fecha_regreso = return_date
        self.db.commit()
        self.db.refresh(prestamo_model)
        return self._to_domain(prestamo_model)

    def approve(self, loan_id: int) -> Optional[Loan]:
        prestamo_model = self.db.get(Prestamo, loan_id)
        if prestamo_model is None:
            return None

        prestamo_model.estado = EstadoPrestamo.ACTIVO
        prestamo_model.fecha_aprobacion = date.today()
        prestamo_model.fecha_vencimiento = date.today() + timedelta(days=prestamo_model.dias_prestamo)
        self.db.commit()
        self.db.refresh(prestamo_model)
        return self._to_domain(prestamo_model)

    def mark_lost(self, loan_id: int) -> Optional[Loan]:
        prestamo_model = self.db.get(Prestamo, loan_id)
        if prestamo_model is None:
            return None

        prestamo_model.estado = EstadoPrestamo.PERDIDO
        self.db.commit()
        self.db.refresh(prestamo_model)
        return self._to_domain(prestamo_model)

    def update_status(self, loan_id: int, status: EstadoPrestamo) -> Optional[Loan]:
        prestamo_model = self.db.get(Prestamo, loan_id)
        if prestamo_model is None:
            return None

        prestamo_model.estado = status
        self.db.commit()
        self.db.refresh(prestamo_model)
        return self._to_domain(prestamo_model)

    def delete(self, loan_id: int) -> bool:
        prestamo_model = self.db.get(Prestamo, loan_id)
        if prestamo_model is None:
            return False

        prestamo_model.estado = EstadoPrestamo.CANCELADO
        self.db.commit()
        return True
