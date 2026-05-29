from __future__ import annotations


def validate_complete_activity(user_id: int | None, goal_id: int | None, workout_day_id: int | None) -> dict:
    errors = []
    if not user_id:
        errors.append("User session is required.")
    if not goal_id:
        errors.append("Active goal is required.")
    if not workout_day_id:
        errors.append("Workout day is required.")
    return {"valid": not errors, "errors": errors}
