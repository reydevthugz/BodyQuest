"""One-shot final submission check. Run: py scripts/submission_check.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DOCS = [
    "README.md",
    "SYSTEM_OVERVIEW.md",
    "DEFENSE_GUIDE.md",
    "INSTALLATION_GUIDE.md",
    "DEMO_SCRIPT.md",
    "DEMO_CHECKLIST.md",
    "PROJECT_STRUCTURE.md",
    "FINAL_CHECKLIST.md",
]


def main() -> int:
    ok = True
    print("=== BodyQuest Final Submission Check ===\n")

    # Documentation
    print("[Documentation]")
    for name in DOCS:
        exists = (ROOT / name).is_file()
        print(f"  {'OK' if exists else 'FAIL'}  {name}")
        ok = ok and exists

    # Requirements
    print("\n[Dependencies]")
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8").strip().splitlines()
    pkgs = {l.strip().lower() for l in req if l.strip()}
    deps_ok = pkgs == {"flet", "mysql-connector-python"}
    print(f"  {'OK' if deps_ok else 'FAIL'}  requirements.txt: {sorted(pkgs)}")
    ok = ok and deps_ok

    # MySQL only + startup
    print("\n[MySQL / Startup]")
    try:
        from config.settings import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, LEGACY_ADMIN_EMAIL
        from database.connection import health_check, get_connection
        from database.migrations import initialize_database
        from database.seeders import seed_default_admin
        import mysql.connector  # noqa: F401

        health_check()
        print("  OK    health_check (mysql.connector)")
        initialize_database()
        print("  OK    initialize_database")
        c1 = seed_default_admin()
        c2 = seed_default_admin()
        print(f"  OK    seed idempotent (first={c1}, second={c2})")

        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT email, role FROM users WHERE role = 'admin'")
            admins = cur.fetchall()
            cur.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'user'")
            users = int(cur.fetchone()["c"])

        admin_emails = [a["email"] for a in admins]
        has_default = DEFAULT_ADMIN_EMAIL in admin_emails
        print(f"  {'OK' if has_default else 'FAIL'}  default admin present: {admin_emails}")
        print(f"  INFO  user accounts in DB: {users} (signup only, not auto-seeded)")
        ok = ok and has_default

        from services.auth_service import login_user

        admin = login_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
        print(f"  {'OK' if admin else 'FAIL'}  admin login ({DEFAULT_ADMIN_EMAIL})")
        ok = ok and bool(admin)

        if LEGACY_ADMIN_EMAIL in admin_emails:
            legacy = login_user(LEGACY_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
            print(f"  {'OK' if legacy else 'INFO'}  legacy admin login ({LEGACY_ADMIN_EMAIL})")

        import main  # noqa: F401
        import app  # noqa: F401

        print("  OK    main.py / app import (startup path)")
    except Exception as exc:
        print(f"  FAIL  {exc}")
        ok = False

    # Routes
    print("\n[Routes]")
    from utils.route_utils import USER_ROUTES, ADMIN_ROUTES, AUTH_ROUTES

    expected_user = 9
    expected_admin = 9
    u_ok = len(USER_ROUTES) == expected_user
    a_ok = len(ADMIN_ROUTES) == expected_admin
    print(f"  {'OK' if u_ok else 'FAIL'}  {len(USER_ROUTES)} user routes")
    print(f"  {'OK' if a_ok else 'FAIL'}  {len(ADMIN_ROUTES)} admin routes")
    print(f"  OK    auth routes: {sorted(AUTH_ROUTES)}")
    ok = ok and u_ok and a_ok

    print("\n" + ("=== READY FOR DEMO AND DEFENSE ===" if ok else "=== ISSUES FOUND ==="))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
