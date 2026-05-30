from __future__ import annotations

from repositories.goal_repository import GoalRepository
from repositories.user_repository import UserRepository
from utils.security import (
    generate_salt,
    hash_password,
    normalize_email,
    sanitize_text,
    verify_password,
)
_user_repo = UserRepository()
_goal_repo = GoalRepository()


def ensure_default_admin() -> None:
    from database.seeders import seed_default_admin

    seed_default_admin()


def _verify_and_maybe_migrate(row: dict, password: str) -> bool:
    plain = (password or "").strip()
    stored_hash = row.get("password_hash")
    stored_salt = row.get("password_salt")

    if stored_hash and stored_salt:
        return verify_password(plain, stored_hash, stored_salt)

    legacy = (row.get("password") or "").strip()
    if legacy and hmac_compare_legacy(legacy, plain):
        salt = generate_salt()
        pwd_hash = hash_password(plain, salt)
        _user_repo.update_password_hash(int(row["id"]), pwd_hash, salt)
        return True
    return False


def hmac_compare_legacy(stored: str, provided: str) -> bool:
    import hmac

    return hmac.compare_digest(stored, provided)


def create_user(full_name: str, email: str, password: str, role: str = "user") -> tuple[bool, str]:
    full_name = sanitize_text(full_name)
    email = normalize_email(email)
    password = (password or "").strip()
    if role != "user":
        return False, "Invalid account type."
    if not full_name or not email or not password:
        return False, "All fields are required."
    if _user_repo.email_exists(email):
        from utils.messages import SIGNUP_EMAIL_EXISTS

        return False, SIGNUP_EMAIL_EXISTS
    try:
        _user_repo.create_user(full_name, email, password, role)
    except Exception as exc:
        print(f"[BODYQUEST] create_user error: {exc}")
        from utils.messages import GENERIC_ERROR

        return False, GENERIC_ERROR
    from utils.messages import SIGNUP_SUCCESS

    return True, SIGNUP_SUCCESS


def login_user(email: str, password: str):
    email = normalize_email(email)
    row = _user_repo.find_by_email(email)
    if not row:
        return None
    if not _verify_and_maybe_migrate(row, password):
        return None
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "role": row["role"],
    }


def authenticate_user(email: str, password: str):
    return login_user(email, password)


def get_user_by_email(email: str):
    return _user_repo.find_by_email(email)


def get_user_by_id(user_id: int):
    return _user_repo.find_by_id(user_id)


def is_admin(user) -> bool:
    return bool(user) and user.get("role") == "admin"


def is_user(user) -> bool:
    return bool(user) and user.get("role") == "user"


def has_active_goal(user_id: int) -> bool:
    return _goal_repo.has_active_goal(user_id)


def user_has_active_goal(user_id: int) -> bool:
    return has_active_goal(user_id)
