from __future__ import annotations

from services.session_service import is_admin_session, is_user_session


def require_admin(page) -> bool:
    return is_admin_session(page)


def require_user(page) -> bool:
    return is_user_session(page)
