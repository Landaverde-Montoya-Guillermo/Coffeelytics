import os
from contextlib import contextmanager
import mysql.connector
from dotenv import load_dotenv

_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_RAIZ_PROYECTO, ".env"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "bd_coffeelytics"),
    "charset": "utf8mb4"
}


def conectar():
    """Devuelve una conexión activa a MySQL."""
    return mysql.connector.connect(**DB_CONFIG)


@contextmanager
def transaccion(dictionary=False):
    """
    Gestor de contexto para transacciones atómicas.
    Abre conexión y cursor; hace commit al salir sin errores o rollback si falla.
    """
    conn = conectar()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()