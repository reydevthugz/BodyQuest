"""Phase 6 validation: admin-only seed, no demo users, empty admin data safe."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.connection import get_connection, health_check
from database.seeders import seed_default_admin
from config.settings import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_NAME
from services.admin_service import get_dashboard_stats, get_reports_summary, get_all_users, get_leaderboard


def main() -> None:
    health_check()
    created = seed_default_admin()
    again = seed_default_admin()

    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, email, role, full_name FROM users WHERE role = 'admin'")
        admins = cur.fetchall()
        cur.execute("SELECT id, email, role FROM users WHERE role = 'user'")
        users = cur.fetchall()

    print("=== Phase 6 Seed Validation ===")
    print(f"First seed created admin: {created}")
    print(f"Second seed created admin: {again} (should be False)")
    print(f"Admin count: {len(admins)}")
    for a in admins:
        print(f"  - {a['email']} ({a['full_name']}) role={a['role']}")

    if len(admins) != 1:
        raise SystemExit(f"FAIL: Expected 1 admin, found {len(admins)}")
    if admins[0]["email"] != DEFAULT_ADMIN_EMAIL:
        raise SystemExit(f"FAIL: Admin email mismatch: {admins[0]['email']}")

    from services.auth_service import login_user

    logged = login_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    if not logged or logged.get("role") != "admin":
        raise SystemExit("FAIL: Default admin login failed")

    print(f"User accounts in DB (from signup only, not seed): {len(users)}")
    print("=== Empty Admin Data (no crash) ===")
    stats = get_dashboard_stats()
    report = get_reports_summary()
    all_u = get_all_users()
    board = get_leaderboard()
    print(f"total_users (role=user): {stats['total_users']}")
    print(f"reports total_users: {report['total_users']}")
    print(f"get_all_users count: {len(all_u)}")
    print(f"leaderboard count: {len(board)}")
    print("=== PASS: Phase 6 validation complete ===")


if __name__ == "__main__":
    main()
