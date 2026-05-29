from __future__ import annotations

from typing import Any

_MEMORY_STORE: dict[str, dict[str, Any]] = {}

_SESSION_KEYS = ("user_id", "user_role", "user_name", "user_email")
_SENSITIVE_KEYS = frozenset({"password", "password_hash", "password_salt"})


def _memory_key(page) -> str:
    sid = getattr(page, "session_id", None)
    return str(sid) if sid else "global"


def _memory_get_store(page) -> dict[str, Any]:
    key = _memory_key(page)
    if key not in _MEMORY_STORE:
        _MEMORY_STORE[key] = {}
    return _MEMORY_STORE[key]


def _set_via_session(page, key: str, value: Any) -> bool:
    session = getattr(page, "session", None)
    if session and hasattr(session, "set"):
        try:
            session.set(key, value)
            return True
        except Exception:
            return False
    return False


def _get_via_session(page, key: str, default: Any = None) -> Any:
    session = getattr(page, "session", None)
    if session and hasattr(session, "get"):
        try:
            value = session.get(key)
            return default if value is None else value
        except Exception:
            return default
    return default


def set_session_value(page, key: str, value: Any) -> None:
    if key in _SENSITIVE_KEYS:
        return
    if _set_via_session(page, key, value):
        return
    if hasattr(page, "data"):
        store = page.data if isinstance(page.data, dict) else {}
        store[key] = value
        page.data = store
        return
    _memory_get_store(page)[key] = value


def get_session_value(page, key: str, default: Any = None) -> Any:
    session_value = _get_via_session(page, key, None)
    if session_value is not None:
        return session_value
    if hasattr(page, "data") and isinstance(page.data, dict):
        data_value = page.data.get(key, None)
        if data_value is not None:
            return data_value
    return _memory_get_store(page).get(key, default)


def clear_session(page) -> None:
    for key in _SESSION_KEYS:
        set_session_value(page, key, None)
    _memory_get_store(page).clear()


def get_current_user_id(page) -> int | None:
    raw = get_session_value(page, "user_id", None)
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def get_current_user_role(page) -> str:
    role = get_session_value(page, "user_role", "")
    return str(role or "")


def get_current_user_name(page) -> str:
    name = get_session_value(page, "user_name", "")
    return str(name or "")


def get_current_user(page):
    user_id = get_current_user_id(page)
    if user_id is None:
        return None
    return {
        "id": user_id,
        "role": get_current_user_role(page),
        "full_name": get_current_user_name(page),
        "email": str(get_session_value(page, "user_email", "") or ""),
    }


def set_current_user(page, user) -> None:
    if not user:
        clear_current_user(page)
        return
    safe = {k: v for k, v in user.items() if k not in _SENSITIVE_KEYS}
    set_session_value(page, "user_id", safe.get("id"))
    set_session_value(page, "user_role", safe.get("role", ""))
    set_session_value(page, "user_name", safe.get("full_name", ""))
    set_session_value(page, "user_email", safe.get("email", ""))


def clear_current_user(page) -> None:
    clear_session(page)


def is_logged_in(page) -> bool:
    return get_current_user_id(page) is not None


def is_admin_logged_in(page) -> bool:
    return is_logged_in(page) and get_current_user_role(page) == "admin"


def is_user_logged_in(page) -> bool:
    return is_logged_in(page) and get_current_user_role(page) == "user"


def is_admin_session(page) -> bool:
    return is_admin_logged_in(page)


def is_user_session(page) -> bool:
    return is_user_logged_in(page)
