"""Cuentas locales del acceso al simulador."""
import hashlib
import hmac
from typing import Optional

from .db import get_conexion


class RepositorioUsuarios:

    def autenticar(self, usuario: str, clave: str) -> Optional[dict]:
        """Devuelve la cuenta si la contraseña coincide."""
        with get_conexion() as conn:
            fila = conn.execute(
                """
                SELECT usuario, nombre, rol, salt, clave_hash
                FROM usuarios
                WHERE usuario = ?
                """,
                (usuario.strip().lower(),),
            ).fetchone()
        if fila is None:
            return None
        calculada = hashlib.pbkdf2_hmac(
            "sha256", clave.encode(), fila["salt"], 120_000
        )
        if not hmac.compare_digest(calculada, fila["clave_hash"]):
            return None
        return {
            "usuario": fila["usuario"],
            "nombre": fila["nombre"],
            "rol": fila["rol"],
        }
