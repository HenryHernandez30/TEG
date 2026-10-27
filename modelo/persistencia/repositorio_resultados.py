from .db import get_conexion


class RepositorioResultados:

    def guardar(self, escenario_id: int, metricas: dict) -> int:
        with get_conexion() as conn:
            cur = conn.execute("""
                INSERT INTO simulaciones
                  (escenario_id, atendidos, espera_promedio,
                   tiempo_total_promedio, longitud_cola_max,
                   utilizacion, throughput)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (escenario_id,
                  metricas["clientes_atendidos"],
                  metricas["espera_promedio"],
                  metricas["tiempo_total_promedio"],
                  metricas["longitud_cola_max"],
                  metricas["utilizacion_operadores"],
                  metricas["throughput"]))
            return cur.lastrowid

    def historial(self, escenario_id: int = None):
        query = """
            SELECT s.*, e.nombre AS escenario,
                   e.num_operadores, e.tasa_llegada, e.tasa_servicio
            FROM simulaciones s
            JOIN escenarios e ON e.id = s.escenario_id
        """
        params = ()
        if escenario_id:
            query += " WHERE s.escenario_id = ?"
            params = (escenario_id,)
        query += " ORDER BY s.ejecutado_en DESC"

        with get_conexion() as conn:
            return [dict(f) for f in conn.execute(query, params).fetchall()]
            