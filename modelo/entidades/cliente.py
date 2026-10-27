from dataclasses import dataclass, field
from enum import Enum

class Prioridad(Enum):
    BAJA = 1
    MEDIA = 2
    ALTA = 3

@dataclass
class Ticket:
    id: int
    tiempo_llegada: float
    prioridad: Prioridad = Prioridad.MEDIA
    tiempo_inicio_servicio: float = None
    tiempo_fin_servicio: float = None
    operador_asignado: int = None

    @property
    def tiempo_espera(self) -> float:
        if self.tiempo_inicio_servicio is None:
            return 0.0
        return self.tiempo_inicio_servicio - self.tiempo_llegada

    @property
    def tiempo_total(self) -> float:
        if self.tiempo_fin_servicio is None:
            return 0.0
        return self.tiempo_fin_servicio - self.tiempo_llegada