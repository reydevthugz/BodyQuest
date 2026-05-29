from __future__ import annotations

from services import achievement_service, plan_service, progress_service


def get_profile_summary(user_id: int) -> dict:
    goal = plan_service.get_active_goal(user_id)
    return {
        "goal": goal,
        "progress_percent": plan_service.get_progress_percentage(goal["id"]) if goal else 0,
        "achievement_count": len(achievement_service.get_user_achievements(user_id)),
        "workout_count": len(progress_service.get_user_workout_history(user_id)),
    }
