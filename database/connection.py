from __future__ import annotations

from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error

from config.settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def _base_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        autocommit=False,
    )


@contextmanager
def get_connection():
    conn = None
    try:
        conn = _base_connection()
        conn.database = DB_NAME
        yield conn
    except Error as exc:
        raise RuntimeError(f"MySQL connection error: {exc}") from exc
    finally:
        if conn and conn.is_connected():
            conn.close()


def close_connection(conn) -> None:
    if conn and conn.is_connected():
        conn.close()


def health_check() -> None:
    conn = None
    try:
        conn = _base_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        row = cur.fetchone()
        if not row or row[0] != 1:
            raise RuntimeError("MySQL health check failed: unexpected SELECT 1 result.")
    except Error as exc:
        raise RuntimeError(f"MySQL health check failed: {exc}") from exc
    finally:
        if conn and conn.is_connected():
            conn.close()
