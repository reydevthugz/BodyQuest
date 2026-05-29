import flet as ft

from app import main as app_main
from database.connection import health_check
from database.migrations import initialize_database
from database.seeders import seed_default_admin


if __name__ == "__main__":
    try:
        print("[GYMBRO] Initializing MySQL database...")
        print("[GYMBRO] Running MySQL health check...")
        health_check()
        print("[GYMBRO] MySQL health check passed (SELECT 1)")
        initialize_database()
        print("[GYMBRO] Database ready: gymbro")

        print("[GYMBRO] Ensuring default admin account only (no demo users)...")
        created = seed_default_admin()
        if created:
            print("[GYMBRO] Default admin created: admin@gymbro.com")
        else:
            print("[GYMBRO] Default admin already exists (no duplicate created)")
    except Exception as exc:
        print(f"[GYMBRO] Startup failed: {exc}")
        print("[GYMBRO] Hint: Make sure Laragon MySQL is running at localhost:3306 (user root, blank password).")
        raise

    print("[GYMBRO] Launching app...")
    if hasattr(ft, "run"):
        ft.run(app_main)
    else:
        ft.app(target=app_main)
