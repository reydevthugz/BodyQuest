from __future__ import annotations

from utils.security import sanitize_text
from utils.validators import is_allowed_goal_type


def validate_goal_selection(goal_type: str) -> dict:
    errors = []
    goal_type = sanitize_text(goal_type or "", max_length=100)
    if not is_allowed_goal_type(goal_type):
        errors.append("Please select a valid fitness goal.")
    return {"valid": not errors, "errors": errors, "goal_type": goal_type}
