from __future__ import annotations

from typing import Any

_MEMORY_STORE: dict[str, dict[str, Any]] = {}
_ONBOARDING_BY_USER: dict[int, dict[str, Any]] = {}

_SESSION_KEYS = ("user_id", "user_role", "user_name", "user_email")
_ONBOARDING_KEYS = frozenset({"selected_goal", "changing_plan"})
_SENSITIVE_KEYS = frozenset({"password", "password_hash", "password_salt"})


def _memory_key(page) -> str:
    sid = getattr(page, "session_id", None)
    return str(sid) if sid else "global"


def _memory_get_store(page) -> dict[str, Any]:
    key = _memory_key(page)
    if key not in _MEMORY_STORE:
        _MEMORY_STORE[key] = {}
    return _MEMORY_STORE[key]


def _ensure_page_data(page) -> dict[str, Any]:
    if not isinstance(getattr(page, "data", None), dict):
        page.data = {}
    return page.data


def _onboarding_user_id(page, key: str, value: Any | None = None) -> int | None:
    if key == "user_id" and value is not None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    raw = None
    store = _ensure_page_data(page)
    if "user_id" in store:
        raw = store["user_id"]
    elif key != "user_id":
        mem = _memory_get_store(page)
        raw = mem.get("user_id")
    if raw is None:
        raw = _get_via_session(page, "user_id", None)
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def _set_onboarding_for_user(user_id: int | None, key: str, value: Any) -> None:
    if user_id is None or key not in _ONBOARDING_KEYS:
        return
    bucket = _ONBOARDING_BY_USER.setdefault(int(user_id), {})
    if value is None or value == "":
        bucket.pop(key, None)
        if not bucket:
            _ONBOARDING_BY_USER.pop(int(user_id), None)
    else:
        bucket[key] = value


def _get_onboarding_for_user(user_id: int | None, key: str, default: Any = None) -> Any:
    if user_id is None or key not in _ONBOARDING_KEYS:
        return default
    bucket = _ONBOARDING_BY_USER.get(int(user_id), {})
    if key in bucket:
        return bucket[key]
    return default


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
    """Persist to Flet session (if any), page.data, memory, and user onboarding store."""
    if key in _SENSITIVE_KEYS:
        return
    _set_via_session(page, key, value)
    store = _ensure_page_data(page)
    store[key] = value
    _memory_get_store(page)[key] = value
    uid = _onboarding_user_id(page, key, value)
    _set_onboarding_for_user(uid, key, value)


def get_session_value(page, key: str, default: Any = None) -> Any:
    """Read user onboarding store, page.data, memory, then Flet session."""
    uid = _onboarding_user_id(page, key)
    if key in _ONBOARDING_KEYS:
        bucket = _ONBOARDING_BY_USER.get(int(uid), {}) if uid is not None else {}
        if key in bucket:
            return bucket[key]
    if hasattr(page, "data") and isinstance(page.data, dict) and key in page.data:
        val = page.data[key]
        if key not in _ONBOARDING_KEYS or (val is not None and val != ""):
            return val
    mem = _memory_get_store(page)
    if key in mem:
        return mem[key]
    session_value = _get_via_session(page, key, None)
    if session_value is not None:
        return session_value
    return default


def clear_session(page) -> None:
    uid = _onboarding_user_id(page, "user_id")
    for key in _SESSION_KEYS:
        set_session_value(page, key, None)
    if uid is not None:
        _ONBOARDING_BY_USER.pop(int(uid), None)
    _memory_get_store(page).clear()
    if isinstance(getattr(page, "data", None), dict):
        for key in list(page.data.keys()):
            if key not in ("user_id", "user_role", "user_name", "user_email"):
                del page.data[key]


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
