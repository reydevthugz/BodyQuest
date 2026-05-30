import flet as ft

from app import main as app_main
from config.settings import DB_NAME, DEFAULT_ADMIN_EMAIL
from database.connection import health_check
from database.migrations import initialize_database
from database.seeders import seed_default_admin


if __name__ == "__main__":
    try:
        print("[BODYQUEST] Initializing MySQL database...")
        print("[BODYQUEST] Running MySQL health check...")
        health_check()
        print("[BODYQUEST] MySQL health check passed (SELECT 1)")
        initialize_database()
        print(f"[BODYQUEST] Database ready: {DB_NAME}")

        print("[BODYQUEST] Ensuring default admin account only (no demo users)...")
        created = seed_default_admin()
        if created:
            print(f"[BODYQUEST] Default admin created: {DEFAULT_ADMIN_EMAIL}")
        else:
            print("[BODYQUEST] Default admin already exists (no duplicate created)")
    except Exception as exc:
        print(f"[BODYQUEST] Startup failed: {exc}")
        print("[BODYQUEST] Hint: Make sure Laragon MySQL is running at localhost:3306 (user root, blank password).")
        raise

    print("[BODYQUEST] Launching app...")
    if hasattr(ft, "run"):
        ft.run(app_main)
    else:
        ft.app(target=app_main)
