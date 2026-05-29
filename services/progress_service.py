from __future__ import annotations

from repositories.goal_repository import GoalRepository
from repositories.progress_repository import ProgressRepository
from repositories.workout_repository import WorkoutRepository
from services.achievement_service import check_and_award_achievements
from utils.messages import (
    ACTIVITY_ALREADY_DONE,
    ACTIVITY_ERROR,
    ACTIVITY_LOCKED,
    ACTIVITY_UNLOCKED,
    PLAN_COMPLETED,
)

_goal_repo = GoalRepository()
_workout_repo = WorkoutRepository()
_progress_repo = ProgressRepository()


def add_progress_log(user_id: int, goal_id: int | None, workout_day_id: int | None, action: str) -> None:
    _progress_repo.add_log(user_id, goal_id, workout_day_id, action)


def unlock_next_day(goal_id: int, current_day_number: int):
    return _workout_repo.unlock_next_day(goal_id, current_day_number)


def mark_goal_completed(goal_id: int) -> None:
    _goal_repo.mark_goal_completed(goal_id)


def is_goal_completed(goal_id: int) -> bool:
    return _goal_repo.is_goal_completed(goal_id)


def get_goal_progress(goal_id: int):
    goal = _goal_repo.get_goal_by_id(goal_id) or {"plan_duration": 0}
    total = int(goal["plan_duration"] or 0)
    completed = _workout_repo.get_completed_days_count(goal_id)
    percent = round((completed / total) * 100) if total else 0
    return {"completed": completed, "total": total, "progress_percent": percent}


def complete_current_day(user_id: int, goal_id: int, workout_day_id: int):
    try:
        if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
            return False, "Workout day not found.", False

        active_goal = _goal_repo.get_active_goal_for_user(user_id, goal_id)
        if not active_goal:
            return False, "No active plan found.", False

        day = _workout_repo.get_workout_day(workout_day_id, goal_id)
        if not day:
            return False, "Workout day not found.", False
        if not day["is_unlocked"]:
            return False, ACTIVITY_LOCKED, False
        if day["is_completed"]:
            return False, ACTIVITY_ALREADY_DONE, False

        current = _workout_repo.get_current_unlocked_day(goal_id)
        if not current or int(current["id"]) != int(workout_day_id):
            return False, ACTIVITY_LOCKED, False

        _workout_repo.mark_day_completed(workout_day_id)
        add_progress_log(user_id, goal_id, workout_day_id, "completed_day")
        next_day = unlock_next_day(goal_id, int(day["day_number"]))
        if not next_day:
            mark_goal_completed(goal_id)
            add_progress_log(user_id, goal_id, workout_day_id, "completed_plan")
            check_and_award_achievements(user_id, goal_id)
            return True, PLAN_COMPLETED, True

        check_and_award_achievements(user_id, goal_id)
        return True, ACTIVITY_UNLOCKED, False
    except Exception as exc:
        print(f"[GYMBRO] complete_current_day error: {exc}")
        return False, ACTIVITY_ERROR, False


def get_user_workout_history(user_id: int):
    return _progress_repo.get_user_workout_history(user_id)


def get_recent_workout_history(user_id: int, limit: int = 5):
    return _progress_repo.get_recent_workout_history(user_id, limit)
