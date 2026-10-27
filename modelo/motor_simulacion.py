import heapq
import random
from typing import List, Optional
from .entidades.cliente import Ticket, Prioridad
from .entidades.operador import Operador


class MotorSimulacion:
    """
    Motor de Simulación de Eventos Discretos (DES).
    Eventos: 'llegada' y 'fin_servicio'.
    """

    def __init__(self, num_operadores: int, tasa_llegada: float,
                 tasa_servicio: float, tiempo_simulacion: float,
                 semilla: int = 42):
        self.num_operadores = num_operadores
        self.lambda_ = tasa_llegada
        self.mu = tasa_servicio
        self.T = tiempo_simulacion
        self.rng = random.Random(semilla)

        self.reloj = 0.0
        self.cola: List[Ticket] = []
        self.operadores = [Operador(id=i) for i in range(num_operadores)]
        self.eventos = []
        self.tickets_completados: List[Ticket] = []
        self.trazas: List[dict] = []
        self._contador_id = 0
        self._cola_max = 0

    def _registrar(self, evento: str, detalle: str, cliente: Optional[int] = None):
        """Guarda una foto del salón después de un movimiento."""
        cola = [t.id for t in self.cola]
        self.trazas.append({
            "t": round(self.reloj, 4),
            "evento": evento,
            "detalle": detalle,
            "cliente": cliente,
            "cola": cola[:14],
            "cola_extra": max(0, len(cola) - 14),
            "mostradores": [
                None if o.ticket_actual is None else o.ticket_actual.id
                for o in self.operadores
            ],
        })

    def _programar_llegada(self):
        t = self.reloj + self.rng.expovariate(self.lambda_)
        if t <= self.T:
            heapq.heappush(self.eventos, (t, 'llegada', None))

    def _programar_fin_servicio(self, operador: Operador):
        t = self.reloj + self.rng.expovariate(self.mu)
        heapq.heappush(self.eventos, (t, 'fin_servicio', operador))

    def _on_llegada(self):
        self._contador_id += 1
        ticket = Ticket(id=self._contador_id, tiempo_llegada=self.reloj,
                        prioridad=Prioridad.MEDIA)
        libre = next((o for o in self.operadores if not o.ocupado), None)
        if libre:
            libre.asignar(ticket, self.reloj)
            self._programar_fin_servicio(libre)
            self._registrar(
                "atencion",
                f"Cliente {ticket.id} pasa al mostrador {libre.id + 1}",
                ticket.id,
            )
        else:
            self.cola.append(ticket)
            self._cola_max = max(self._cola_max, len(self.cola))
            self._registrar(
                "llegada",
                f"Cliente {ticket.id} entra a la fila",
                ticket.id,
            )
        self._programar_llegada()

    def _on_fin_servicio(self, operador: Operador):
        ticket = operador.ticket_actual
        mostrador = operador.id + 1
        operador.liberar(self.reloj)
        if ticket is not None:
            self.tickets_completados.append(ticket)
            self._registrar(
                "salida",
                f"Cliente {ticket.id} sale del mostrador {mostrador}",
                ticket.id,
            )

        if self.cola:
            siguiente = self.cola.pop(0)
            operador.asignar(siguiente, self.reloj)
            self._programar_fin_servicio(operador)
            self._registrar(
                "atencion",
                f"Cliente {siguiente.id} pasa al mostrador {mostrador}",
                siguiente.id,
            )

    def ejecutar(self) -> dict:
        self._registrar("apertura", "La oficina abre")
        self._programar_llegada()
        while self.eventos:
            t, tipo, payload = heapq.heappop(self.eventos)
            if t > self.T:
                break
            self.reloj = t
            if tipo == 'llegada':
                self._on_llegada()
            elif tipo == 'fin_servicio':
                self._on_fin_servicio(payload)
        self._cerrar_horizonte()
        return self.recolectar_metricas()

    def _cerrar_horizonte(self):
        """Cuenta hasta el horizonte el servicio que sigue en curso."""
        for operador in self.operadores:
            ticket = operador.ticket_actual
            if (
                operador.ocupado
                and ticket is not None
                and ticket.tiempo_inicio_servicio is not None
            ):
                operador.tiempo_total_ocupado += max(
                    0.0, self.T - ticket.tiempo_inicio_servicio
                )

    def recolectar_metricas(self) -> dict:
        esperas = [t.tiempo_espera for t in self.tickets_completados if t]
        totales = [t.tiempo_total for t in self.tickets_completados if t]
        horizonte = self.num_operadores * self.T
        ocupacion = (
            sum(o.tiempo_total_ocupado for o in self.operadores) / horizonte
            if horizonte else 0
        )
        return {
            "clientes_atendidos": len(self.tickets_completados),
            "espera_promedio": sum(esperas) / len(esperas) if esperas else 0,
            "tiempo_total_promedio": sum(totales) / len(totales) if totales else 0,
            "longitud_cola_max": self._cola_max,
            "utilizacion_operadores": ocupacion,
            "throughput": len(self.tickets_completados) / self.T if self.T else 0
        }