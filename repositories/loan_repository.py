from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select

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
            aproval_date=prestamo_model.fecha_aprobacion,
            due_date=prestamo_model.fecha_vencimiento,
            retrival_date=prestamo_model.fecha_regreso,
            status=prestamo_model.estado,
        )

    def _to_model(self, loan_entity: Loan) -> Prestamo:
        return Prestamo(
            id_usuario_asociado=loan_entity.user_id,
            codigo_ejemplar=loan_entity.copy_code,
            fecha_aprobacion=loan_entity.aproval_date,
            fecha_vencimiento=loan_entity.due_date,
            fecha_regreso=loan_entity.retrival_date,
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

    def get_model_by_id(self, loan_id: int) -> Optional[Prestamo]:
        return self.db.get(Prestamo, loan_id)

    def list_all(self) -> Sequence[Loan]:
        stmt = select(Prestamo)
        prestamos = self.db.execute(stmt).scalars().all()
        return [self._to_domain(prestamo) for prestamo in prestamos]

    def list_by_user_id(self, user_id: int) -> Sequence[Loan]:
        stmt = select(Prestamo).where(Prestamo.id_usuario_asociado == user_id)
        prestamos = self.db.execute(stmt).scalars().all()
        return [self._to_domain(prestamo) for prestamo in prestamos]

    def list_by_copy_code(self, copy_code: str) -> Sequence[Loan]:
        stmt = select(Prestamo).where(Prestamo.codigo_ejemplar == copy_code)
        prestamos = self.db.execute(stmt).scalars().all()
        return [self._to_domain(prestamo) for prestamo in prestamos]

    def get_active_by_copy_code(self, copy_code: str) -> Optional[Loan]:
        stmt = select(Prestamo).where(
            Prestamo.codigo_ejemplar == copy_code,
            Prestamo.estado.in_([EstadoPrestamo.ACTIVO, EstadoPrestamo.PENDIENTE, EstadoPrestamo.VENCIDO]),
        )
        prestamo_model = self.db.execute(stmt).scalars().first()
        if prestamo_model is None:
            return None
        return self._to_domain(prestamo_model)

    def update(self, loan_id: int, loan_entity: Loan) -> Optional[Loan]:
        prestamo_model = self.db.get(Prestamo, loan_id)
        if prestamo_model is None:
            return None

        prestamo_model.id_usuario_asociado = loan_entity.user_id
        prestamo_model.codigo_ejemplar = loan_entity.copy_code
        prestamo_model.fecha_aprobacion = loan_entity.aproval_date
        prestamo_model.fecha_vencimiento = loan_entity.due_date
        prestamo_model.fecha_regreso = loan_entity.retrival_date
        prestamo_model.estado = loan_entity.status

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

        self.db.delete(prestamo_model)
        self.db.commit()
        return True
