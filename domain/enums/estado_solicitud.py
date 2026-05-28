from enum import Enum

class EstadoSolicitud(Enum):
    PENDIENTE = "pendiente"
    NOTIFICADA = "notificada"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
