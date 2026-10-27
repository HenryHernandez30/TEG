from dataclasses import dataclass, field
from typing import Optional
from .cliente import Ticket

@dataclass
class Operador:
    id: int
    ocupado: bool = False
    ticket_actual: Optional[Ticket] = None
    tiempo_total_ocupado: float = 0.0
    tickets_atendidos: int = 0

    def asignar(self, ticket: Ticket, tiempo_actual: float):
        self.ocupado = True
        self.ticket_actual = ticket
        ticket.tiempo_inicio_servicio = tiempo_actual
        ticket.operador_asignado = self.id

    def liberar(self, tiempo_actual: float):
        if self.ticket_actual:
            self.ticket_actual.tiempo_fin_servicio = tiempo_actual
            self.tiempo_total_ocupado += (
                tiempo_actual - self.ticket_actual.tiempo_inicio_servicio
            )
            self.tickets_atendidos += 1
        self.ocupado = False
        self.ticket_actual = None