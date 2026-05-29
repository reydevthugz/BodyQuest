"""Backward-compatible database entry points."""

from database.connection import get_connection, health_check
from database.migrations import initialize_database
from database.seeders import seed_default_admin

ensure_default_admin = seed_default_admin

__all__ = [
    "get_connection",
    "health_check",
    "initialize_database",
    "seed_default_admin",
    "ensure_default_admin",
]
