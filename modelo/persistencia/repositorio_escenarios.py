from dataclasses import dataclass
from typing import List, Optional
from .db import get_conexion


@dataclass
class Escenario:
    nombre: str
    num_operadores: int
    tasa_llegada: float
    tasa_servicio: float
    horizonte: float
    descripcion: str = ""
    id: Optional[int] = None
    creado_en: Optional[str] = None      # ⬅️ LÍNEA AÑADIDA


class RepositorioEscenarios:

    def guardar(self, esc: Escenario) -> int:
        with get_conexion() as conn:
            cur = conn.execute("""
                INSERT INTO escenarios
                  (nombre, descripcion, num_operadores,
                   tasa_llegada, tasa_servicio, horizonte)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(nombre) DO UPDATE SET
                  descripcion   = excluded.descripcion,
                  num_operadores = excluded.num_operadores,
                  tasa_llegada  = excluded.tasa_llegada,
                  tasa_servicio = excluded.tasa_servicio,
                  horizonte     = excluded.horizonte
                RETURNING id
            """, (esc.nombre, esc.descripcion, esc.num_operadores,
                  esc.tasa_llegada, esc.tasa_servicio, esc.horizonte))
            return cur.fetchone()["id"]

    def listar(self) -> List[Escenario]:
        with get_conexion() as conn:
            filas = conn.execute(
                "SELECT * FROM escenarios ORDER BY creado_en DESC"
            ).fetchall()
        return [Escenario(**{k: f[k] for k in f.keys()}) for f in filas]

    def obtener(self, escenario_id: int) -> Optional[Escenario]:
        with get_conexion() as conn:
            f = conn.execute(
                "SELECT * FROM escenarios WHERE id = ?", (escenario_id,)
            ).fetchone()
        return Escenario(**{k: f[k] for k in f.keys()}) if f else None

    def eliminar(self, escenario_id: int):
        with get_conexion() as conn:
            conn.execute("DELETE FROM escenarios WHERE id = ?", (escenario_id,))