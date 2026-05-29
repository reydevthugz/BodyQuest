"""Phase 8 validation: password hashing, admin login, migration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
from database.connection import get_connection, health_check
from database.migrations import initialize_database
from services.auth_service import login_user
from utils.security import verify_password


def main() -> None:
    health_check()
    initialize_database()

    user = login_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    if not user or user.get("role") != "admin":
        raise SystemExit("FAIL: Admin login failed")

    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT email, password_hash, password_salt, password FROM users WHERE email = %s",
            (DEFAULT_ADMIN_EMAIL,),
        )
        row = cur.fetchone()

    if not row or not row.get("password_hash") or not row.get("password_salt"):
        raise SystemExit("FAIL: Admin password not hashed")

    if not verify_password(DEFAULT_ADMIN_PASSWORD, row["password_hash"], row["password_salt"]):
        raise SystemExit("FAIL: Admin hash verification failed")

    print("=== Phase 8 Security Validation ===")
    print("Admin login: OK")
    print("Password hashed: OK")
    print("Legacy password column cleared or unused:", (row.get("password") or "") == "")
    print("=== PASS ===")


if __name__ == "__main__":
    main()
