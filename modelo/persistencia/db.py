import hashlib
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "datos" / "simulador.db"


def get_conexion() -> sqlite3.Connection:
    """Devuelve una conexión SQLite con foreign keys activadas."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row       # acceso por nombre de columna
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_bd():
    """Crea las tablas si no existen. Llamar al arrancar la app."""
    with get_conexion() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS escenarios (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre        TEXT NOT NULL UNIQUE,
            descripcion   TEXT,
            num_operadores INTEGER NOT NULL,
            tasa_llegada  REAL NOT NULL,
            tasa_servicio REAL NOT NULL,
            horizonte     REAL NOT NULL,
            creado_en     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS simulaciones (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            escenario_id           INTEGER NOT NULL,
            ejecutado_en           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atendidos              INTEGER,
            espera_promedio        REAL,
            tiempo_total_promedio  REAL,
            longitud_cola_max      INTEGER,
            utilizacion            REAL,
            throughput             REAL,
            FOREIGN KEY (escenario_id) REFERENCES escenarios(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_sim_escenario
            ON simulaciones(escenario_id);

        CREATE TABLE IF NOT EXISTS usuarios (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario    TEXT NOT NULL UNIQUE,
            nombre     TEXT NOT NULL,
            rol        TEXT NOT NULL,
            salt       BLOB NOT NULL,
            clave_hash BLOB NOT NULL
        );
        """)
        _asegurar_columnas(conn)
        _asegurar_usuarios(conn)


def _asegurar_columnas(conn: sqlite3.Connection):
    """Añade columnas nuevas si la tabla ya existía con el esquema anterior."""
    existentes = {
        fila[1] for fila in conn.execute("PRAGMA table_info(simulaciones)")
    }
    columnas = {
        "tiempo_total_promedio": "REAL",
        "longitud_cola_max": "INTEGER",
    }
    for nombre, tipo in columnas.items():
        if nombre not in existentes:
            conn.execute(
                f"ALTER TABLE simulaciones ADD COLUMN {nombre} {tipo}"
            )


def _asegurar_usuarios(conn: sqlite3.Connection):
    """Crea las cuentas de demostración solo si la tabla está vacía."""
    total = conn.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()["n"]
    if total:
        return
    cuentas = (
        ("analista", "Analista de operaciones", "Analista"),
        ("supervisor", "Supervisor de sala", "Supervisor"),
        ("admin", "Administrador del sistema", "Administrador"),
    )
    for usuario, nombre, rol in cuentas:
        salt = os.urandom(16)
        clave = hashlib.pbkdf2_hmac("sha256", b"Simop2026", salt, 120_000)
        conn.execute(
            """
            INSERT INTO usuarios (usuario, nombre, rol, salt, clave_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usuario, nombre, rol, salt, clave),
        )
        