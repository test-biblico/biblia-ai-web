"""HEOS_DATABASE — capa de acceso a datos (FASE 2 del manual 040).

SQLite puro, sin dependencias externas. Una sola empresa por base de datos.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "heos.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Crea el esquema si no existe."""
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        conn = get_conn()
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()


def reset_db() -> None:
    """Borra y recrea la base (usado por carga de datos de ejemplo)."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()


# ---------- helpers de lectura ----------
def q(sql: str, params=()):
    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def q1(sql: str, params=()):
    rows = q(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params=()):
    conn = get_conn()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


def insert_many(table: str, cols, rows):
    if not rows:
        return
    placeholders = ", ".join(["?"] * len(cols))
    col_sql = ", ".join(cols)
    conn = get_conn()
    conn.executemany(
        f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders})", rows
    )
    conn.commit()
    conn.close()
