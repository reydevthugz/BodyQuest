from __future__ import annotations

from models.goal_model import GOAL_TYPES
from models.user_model import ROLE_ADMIN, ROLE_USER

ALLOWED_ROLES = {ROLE_ADMIN, ROLE_USER}
ALLOWED_GOAL_TYPES = set(GOAL_TYPES)
ALLOWED_USER_STATUS_FILTERS = {
    "All Users",
    "Active",
    "Inactive",
    "Completed Goal",
    "Changed Plan",
}
ALLOWED_ACHIEVEMENT_BADGE_FILTERS = {
    "All",
    "starter",
    "streak",
    "consistency",
    "cardio",
    "strength",
    "flexibility",
    "champion",
    "switch",
}


def is_allowed_role(role: str) -> bool:
    return role in ALLOWED_ROLES


def is_allowed_goal_type(goal_type: str) -> bool:
    return goal_type in ALLOWED_GOAL_TYPES


def normalize_status_filter(value: str | None) -> str:
    cleaned = (value or "All Users").strip()
    return cleaned if cleaned in ALLOWED_USER_STATUS_FILTERS else "All Users"


def normalize_badge_filter(value: str | None) -> str:
    cleaned = (value or "All").strip()
    return cleaned if cleaned in ALLOWED_ACHIEVEMENT_BADGE_FILTERS else "All"
