from enum import Enum

class EstadoSolicitud(Enum):
    PENDIENTE = "PENDIENTE"
    NOTIFICADA = "NOTIFICADA"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
