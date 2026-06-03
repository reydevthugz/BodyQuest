from __future__ import annotations

from models.goal_model import GOAL_DESCRIPTIONS, GOAL_DURATIONS
from models.workout_model import GOAL_TEMPLATES
from repositories.goal_repository import GoalRepository
from repositories.workout_repository import WorkoutRepository
from services.achievement_service import award_achievement
from services.progress_service import add_progress_log
from utils.validators import is_allowed_goal_type

_goal_repo = GoalRepository()
_workout_repo = WorkoutRepository()

GOAL_DURATIONS = GOAL_DURATIONS
GOAL_DESCRIPTIONS = GOAL_DESCRIPTIONS
GOAL_TEMPLATES = GOAL_TEMPLATES


def get_goal_duration(goal_type: str) -> int:
    return GOAL_DURATIONS.get(goal_type, 30)


def get_goal_description(goal_type: str) -> str:
    return GOAL_DESCRIPTIONS.get(goal_type, "Beginner fitness plan.")


def generate_plan_days(goal_type: str, duration: int):
    templates = GOAL_TEMPLATES.get(goal_type, GOAL_TEMPLATES["General Fitness"])
    result = []
    for day in range(1, duration + 1):
        tpl = templates[(day - 1) % len(templates)]
        result.append(
            {
                "day_number": day,
                "title": tpl[0],
                "description": tpl[1],
                "warmup": tpl[2],
                "main_activity": tpl[3],
                "cooldown": tpl[4],
                "safety_tip": tpl[5],
                "estimated_minutes": tpl[6],
                "is_unlocked": day == 1,
                "is_completed": False,
                "status": "current" if day == 1 else "locked",
            }
        )
    return result


def clear_incomplete_active_goal(user_id: int) -> None:
    """Remove broken active goals that have no workout_days (failed prior start)."""
    active = _goal_repo.get_active_goal(user_id)
    if not active:
        return
    if _workout_repo.count_workout_days(int(active["id"])) == 0:
        _goal_repo.mark_active_goal_replaced(user_id)


def create_new_goal_plan(user_id: int, goal_type: str) -> int:
    if not is_allowed_goal_type(goal_type):
        raise ValueError("Invalid goal type.")
    clear_incomplete_active_goal(user_id)
    duration = get_goal_duration(goal_type)
    plan_days = generate_plan_days(goal_type, duration)
    goal_id = _goal_repo.create_goal(user_id, goal_type, duration)
    try:
        _workout_repo.create_workout_days(goal_id, plan_days)
    except Exception:
        _goal_repo.mark_active_goal_replaced(user_id)
        raise
    return goal_id


def get_active_goal(user_id: int):
    return _goal_repo.get_active_goal(user_id)


def get_latest_completed_goal(user_id: int):
    return _goal_repo.get_latest_completed_goal(user_id)


def get_goal_by_id(goal_id: int):
    return _goal_repo.get_goal_by_id(goal_id)


def get_workout_days(goal_id: int):
    return _workout_repo.get_workout_days(goal_id)


def get_current_unlocked_day(goal_id: int):
    return _workout_repo.get_current_unlocked_day(goal_id)


def get_completed_days_count(goal_id: int) -> int:
    return _workout_repo.get_completed_days_count(goal_id)


def get_progress_percentage(goal_id: int) -> int:
    goal = get_goal_by_id(goal_id)
    if not goal:
        return 0
    completed = get_completed_days_count(goal_id)
    duration = int(goal.get("plan_duration") or 0)
    if duration <= 0:
        return 0
    return round((completed / duration) * 100)


def replace_active_goal(user_id: int) -> int:
    return _goal_repo.mark_active_goal_replaced(user_id)


def confirm_plan_change(user_id: int) -> bool:
    active = get_active_goal(user_id)
    if not active:
        return False
    replace_active_goal(user_id)
    award_achievement(
        user_id=user_id,
        goal_id=None,
        name="Plan Switcher",
        description="Replaced an active plan with a new beginner plan.",
        badge_type="switch",
    )
    add_progress_log(user_id, int(active["id"]), None, "replaced_plan")
    return True


def start_new_plan(user_id: int, goal_type: str) -> int:
    if not is_allowed_goal_type(goal_type):
        raise ValueError("Invalid goal type.")
    clear_incomplete_active_goal(user_id)
    if get_active_goal(user_id):
        raise ValueError("Active plan exists. Use change plan before starting a new one.")
    goal_id = create_new_goal_plan(user_id, goal_type)
    add_progress_log(user_id, goal_id, None, "started_plan")
    day1 = _workout_repo.get_current_unlocked_day(goal_id)
    if not day1:
        raise RuntimeError("Day 1 was not created correctly. Please try Start Plan again.")
    _workout_repo.set_selected_day(goal_id, int(day1["id"]))
    return goal_id
