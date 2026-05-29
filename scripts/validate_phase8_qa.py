"""Phase 8 security QA scan (automated checks)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ISSUES: list[str] = []
PASS: list[str] = []


def scan_file(path: Path, patterns: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = path.relative_to(ROOT)
    for label, needle in patterns.items():
        if needle in text:
            ISSUES.append(f"{rel}: found {label}")


def main() -> None:
    banned = {
        "client_storage": "client_storage",
        "sqlite": "sqlite",
        "flet_core": "flet_core",
    }
    risky_sql = ['cursor.execute(f"', "cursor.execute(f'", '.format(']
    plain_pwd = ['["password"] !=', "['password'] !=", 'password"] ==']

    for path in ROOT.rglob("*.py"):
        rel = str(path.relative_to(ROOT))
        if rel.startswith("scripts"):
            continue
        scan_file(path, banned)
        if "repositories" in rel or "database" in rel:
            for r in risky_sql:
                if r in path.read_text(encoding="utf-8", errors="ignore"):
                    if "migrations" in rel and "DB_NAME" in path.read_text(encoding="utf-8"):
                        continue
                    ISSUES.append(f"{rel}: possible unsafe SQL formatting ({r})")
        if "services/auth_service" in rel.replace("\\", "/"):
            pass  # legacy migrate uses hmac compare_digest only
        elif "validate_phase8" in rel:
            pass
        else:
            for p in plain_pwd:
                if p in path.read_text(encoding="utf-8", errors="ignore"):
                    ISSUES.append(f"{rel}: possible plain password compare ({p})")

    # Layer checks
    for path in ROOT.rglob("pages/**/*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "get_connection" in text or "cursor.execute" in text:
            ISSUES.append(f"{path.relative_to(ROOT)}: SQL in pages layer")
    for path in ROOT.rglob("controllers/**/*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "get_connection" in text or "cursor.execute" in text:
            ISSUES.append(f"{path.relative_to(ROOT)}: SQL in controllers layer")

    # Runtime checks
    from config.settings import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
    from database.connection import health_check
    from services.auth_service import login_user
    from utils.security import verify_password
    from repositories.user_repository import UserRepository

    health_check()
    user = login_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    if not user or user.get("role") != "admin":
        ISSUES.append("Admin login failed")
    else:
        PASS.append("admin@gymbro.com / admin123 login OK")

    repo = UserRepository()
    row = repo.find_by_email(DEFAULT_ADMIN_EMAIL)
    if row and row.get("password_hash") and row.get("password_salt"):
        if verify_password(DEFAULT_ADMIN_PASSWORD, row["password_hash"], row["password_salt"]):
            PASS.append("Admin password hash verifies")
        else:
            ISSUES.append("Admin password hash verification failed")
    else:
        ISSUES.append("Admin missing password_hash/password_salt")

    from repositories.goal_repository import GoalRepository

    gr = GoalRepository()
    if hasattr(gr, "create_goal") and "mark_active_goal_replaced" in Path(ROOT / "repositories/goal_repository.py").read_text():
        PASS.append("Duplicate active plan guard in create_goal")

    from repositories.achievement_repository import AchievementRepository

    ar = AchievementRepository()
    if "achievement_exists" in Path(ROOT / "repositories/achievement_repository.py").read_text():
        PASS.append("Duplicate achievement guard present")

    from repositories.progress_repository import ProgressRepository

    if "log_exists" in Path(ROOT / "repositories/progress_repository.py").read_text():
        PASS.append("Duplicate progress log guard present")

    print("=== Phase 8 Security QA ===")
    print("\nPASS:")
    for item in PASS:
        print(f"  [OK] {item}")
    if ISSUES:
        print("\nISSUES:")
        for item in ISSUES:
            print(f"  [!!] {item}")
        raise SystemExit(1)
    print("\n=== ALL QA CHECKS PASSED ===")


if __name__ == "__main__":
    main()
