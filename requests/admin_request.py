from __future__ import annotations

from utils.security import sanitize_text
from utils.validators import normalize_badge_filter, normalize_status_filter


def validate_user_id(user_id) -> dict:
    errors = []
    try:
        uid = int(user_id)
        if uid <= 0:
            errors.append("Invalid user id.")
    except (TypeError, ValueError):
        errors.append("Invalid user id.")
    return {"valid": not errors, "errors": errors}


def validate_user_search(search: str | None) -> str | None:
    if not search:
        return None
    cleaned = sanitize_text(search, max_length=100)
    return cleaned or None


def validate_status_filter(status_filter: str | None) -> str:
    return normalize_status_filter(status_filter)


def validate_badge_filter(badge_filter: str | None) -> str:
    return normalize_badge_filter(badge_filter)
