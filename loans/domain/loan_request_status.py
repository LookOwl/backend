from enum import Enum

class LoanRequestStatus(Enum):
    PENDIENTE = "PENDIENTE"
    CANCELADA = "CANCELADA"
    ASIGNADA = "ASIGNADA"
    NOTIFICADA = "NOTIFICADA"
    COMPLETADA = "COMPLETADA"
