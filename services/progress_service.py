from __future__ import annotations

from repositories.goal_repository import GoalRepository
from repositories.progress_repository import ProgressRepository
from repositories.workout_repository import WorkoutRepository
from services.achievement_service import check_and_award_achievements
from services.session_service import get_session_value, set_session_value
from utils.messages import (
    ACTIVITY_ALREADY_DONE,
    ACTIVITY_ERROR,
    ACTIVITY_LOCKED,
    NO_ACTIVE_PLAN,
    PLAN_COMPLETED,
    TASK_LOCKED,
    TASK_STARTED,
    TASK_STOPPED,
    TIMER_REQUIRED,
    WEEKLY_TASK_PROGRESS,
    day_unlocked_message,
)

_goal_repo = GoalRepository()
_workout_repo = WorkoutRepository()
_progress_repo = ProgressRepository()


def resolve_day_status(day: dict) -> str:
    if day.get("is_completed"):
        return "completed"
    if not day.get("is_unlocked"):
        return "locked"
    db_status = str(day.get("status") or "").lower()
    if db_status == "stopped":
        return "stopped"
    if db_status == "in_progress" or day.get("started_at"):
        return "in_progress"
    return "current"


def add_progress_log(
    user_id: int,
    goal_id: int | None,
    workout_day_id: int | None,
    action: str,
    duration_seconds: int = 0,
) -> None:
    _progress_repo.add_log(user_id, goal_id, workout_day_id, action, duration_seconds)


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


def get_timeline_days(goal_id: int) -> list[dict]:
    days = _workout_repo.get_workout_days(goal_id)
    result = []
    for day in days:
        enriched = dict(day)
        enriched["display_status"] = resolve_day_status(enriched)
        result.append(enriched)
    return result


def select_timeline_day(user_id: int, goal_id: int, workout_day_id: int, page) -> tuple[bool, str, str | None]:
    if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
        return False, "Workout day not found.", None
    active_goal = _goal_repo.get_active_goal_for_user(user_id, goal_id)
    if not active_goal:
        return False, NO_ACTIVE_PLAN, None

    day = _workout_repo.get_workout_day(workout_day_id, goal_id)
    if not day:
        return False, "Workout day not found.", None

    status = resolve_day_status(day)
    if status == "locked":
        return False, TASK_LOCKED, None
    if status == "completed":
        set_session_value(page, "view_workout_day_id", int(workout_day_id))
        set_session_value(page, "selected_workout_day_id", None)
        return True, "", "view"

    current = _workout_repo.get_current_unlocked_day(goal_id)
    if not current or int(current["id"]) != int(workout_day_id):
        return False, TASK_LOCKED, None
    if status not in ("current", "in_progress", "stopped"):
        return False, TASK_LOCKED, None

    set_session_value(page, "selected_workout_day_id", int(workout_day_id))
    set_session_value(page, "view_workout_day_id", None)
    _workout_repo.set_selected_day(goal_id, int(workout_day_id))
    return True, "", "active"


def get_activity_day(user_id: int, goal_id: int, page) -> tuple[dict | None, bool]:
    if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
        return None, False

    view_id = get_session_value(page, "view_workout_day_id", None)
    if view_id:
        day = _workout_repo.get_workout_day(int(view_id), goal_id)
        if day and day.get("is_completed"):
            return day, True

    selected_id = get_session_value(page, "selected_workout_day_id", None)
    if selected_id:
        day = _workout_repo.get_workout_day(int(selected_id), goal_id)
        current = _workout_repo.get_current_unlocked_day(goal_id)
        if day and current and int(day["id"]) == int(current["id"]):
            return day, False

    db_selected = _workout_repo.get_selected_day(goal_id)
    current = _workout_repo.get_current_unlocked_day(goal_id)
    if db_selected and current and int(db_selected["id"]) == int(current["id"]):
        return db_selected, False
    if current:
        return current, False
    return None, False


def clear_activity_session(page) -> None:
    set_session_value(page, "selected_workout_day_id", None)
    set_session_value(page, "view_workout_day_id", None)


def start_task_timer(user_id: int, goal_id: int, workout_day_id: int) -> tuple[bool, str]:
    if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
        return False, "Workout day not found."
    active_goal = _goal_repo.get_active_goal_for_user(user_id, goal_id)
    if not active_goal:
        return False, NO_ACTIVE_PLAN

    day = _workout_repo.get_workout_day(workout_day_id, goal_id)
    if not day:
        return False, "Workout day not found."
    if day.get("is_completed"):
        return False, ACTIVITY_ALREADY_DONE
    if not day.get("is_unlocked"):
        return False, ACTIVITY_LOCKED

    current = _workout_repo.get_current_unlocked_day(goal_id)
    if not current or int(current["id"]) != int(workout_day_id):
        return False, TASK_LOCKED

    if not day.get("started_at"):
        _workout_repo.mark_day_started(workout_day_id)
    elif resolve_day_status(day) == "stopped":
        _workout_repo.mark_day_resumed(workout_day_id)
    return True, ""


def stop_task(user_id: int, goal_id: int, workout_day_id: int) -> tuple[bool, str]:
    if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
        return False, "Workout day not found."
    active_goal = _goal_repo.get_active_goal_for_user(user_id, goal_id)
    if not active_goal:
        return False, NO_ACTIVE_PLAN

    day = _workout_repo.get_workout_day(workout_day_id, goal_id)
    if not day:
        return False, "Workout day not found."
    if day.get("is_completed"):
        return False, ACTIVITY_ALREADY_DONE
    if not day.get("is_unlocked"):
        return False, ACTIVITY_LOCKED
    if not day.get("started_at"):
        return False, TIMER_REQUIRED

    current = _workout_repo.get_current_unlocked_day(goal_id)
    if not current or int(current["id"]) != int(workout_day_id):
        return False, TASK_LOCKED

    status = resolve_day_status(day)
    if status not in ("in_progress", "stopped"):
        return False, ACTIVITY_LOCKED

    _workout_repo.mark_day_stopped(workout_day_id)
    return True, TASK_STOPPED


def start_timeline_task(user_id: int, goal_id: int, workout_day_id: int, page) -> tuple[bool, str]:
    if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
        return False, "Workout day not found."
    active_goal = _goal_repo.get_active_goal_for_user(user_id, goal_id)
    if not active_goal:
        return False, NO_ACTIVE_PLAN

    day = _workout_repo.get_workout_day(workout_day_id, goal_id)
    if not day:
        return False, "Workout day not found."
    status = resolve_day_status(day)
    if status == "locked":
        return False, TASK_LOCKED
    if status == "completed":
        return False, ACTIVITY_ALREADY_DONE

    ok, msg, mode = select_timeline_day(user_id, goal_id, workout_day_id, page)
    if not ok:
        return False, msg
    if mode == "view":
        return True, ""
    if status == "in_progress":
        return True, ""

    timer_ok, timer_msg = start_task_timer(user_id, goal_id, workout_day_id)
    if not timer_ok:
        return False, timer_msg
    return True, TASK_STARTED


def continue_timeline_task(user_id: int, goal_id: int, workout_day_id: int, page) -> tuple[bool, str]:
    if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
        return False, "Workout day not found."
    active_goal = _goal_repo.get_active_goal_for_user(user_id, goal_id)
    if not active_goal:
        return False, NO_ACTIVE_PLAN

    day = _workout_repo.get_workout_day(workout_day_id, goal_id)
    if not day:
        return False, "Workout day not found."
    status = resolve_day_status(day)
    if status != "in_progress":
        return False, TASK_LOCKED
    ok, msg, _mode = select_timeline_day(user_id, goal_id, workout_day_id, page)
    if not ok:
        return False, msg
    return True, ""


def resume_timeline_task(user_id: int, goal_id: int, workout_day_id: int, page) -> tuple[bool, str]:
    if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
        return False, "Workout day not found."
    active_goal = _goal_repo.get_active_goal_for_user(user_id, goal_id)
    if not active_goal:
        return False, NO_ACTIVE_PLAN

    day = _workout_repo.get_workout_day(workout_day_id, goal_id)
    if not day:
        return False, "Workout day not found."
    if resolve_day_status(day) != "stopped":
        return False, TASK_LOCKED

    ok, msg, _mode = select_timeline_day(user_id, goal_id, workout_day_id, page)
    if not ok:
        return False, msg
    timer_ok, timer_msg = start_task_timer(user_id, goal_id, workout_day_id)
    if not timer_ok:
        return False, timer_msg
    return True, ""


def complete_current_day(
    user_id: int,
    goal_id: int,
    workout_day_id: int,
    actual_duration_seconds: int = 0,
):
    try:
        if not _goal_repo.goal_belongs_to_user(goal_id, user_id):
            return False, "Workout day not found.", False

        active_goal = _goal_repo.get_active_goal_for_user(user_id, goal_id)
        if not active_goal:
            return False, NO_ACTIVE_PLAN, False

        day = _workout_repo.get_workout_day(workout_day_id, goal_id)
        if not day:
            return False, "Workout day not found.", False
        if not day["is_unlocked"]:
            return False, ACTIVITY_LOCKED, False
        if day["is_completed"]:
            return False, ACTIVITY_ALREADY_DONE, False

        status = resolve_day_status(day)
        if status == "locked":
            return False, ACTIVITY_LOCKED, False
        if status not in ("current", "in_progress", "stopped"):
            return False, ACTIVITY_LOCKED, False
        if not day.get("started_at"):
            return False, TIMER_REQUIRED, False

        current = _workout_repo.get_current_unlocked_day(goal_id)
        if not current or int(current["id"]) != int(workout_day_id):
            return False, ACTIVITY_LOCKED, False

        completed_before = _workout_repo.get_completed_days_count(goal_id)
        duration = int(actual_duration_seconds or 0)
        _workout_repo.mark_day_completed(workout_day_id, duration)
        add_progress_log(user_id, goal_id, workout_day_id, "completed_day", duration)
        next_day = unlock_next_day(goal_id, int(day["day_number"]))

        if not next_day:
            mark_goal_completed(goal_id)
            add_progress_log(user_id, goal_id, workout_day_id, "completed_plan", duration)
            check_and_award_achievements(user_id, goal_id)
            return True, PLAN_COMPLETED, True

        check_and_award_achievements(user_id, goal_id)
        completed_after = _workout_repo.get_completed_days_count(goal_id)
        next_num = int(next_day.get("day_number") or 0)
        message = day_unlocked_message(next_num) if next_num else "Great job! The next task is now unlocked."
        if completed_before < 7 <= completed_after:
            message = f"{message} {WEEKLY_TASK_PROGRESS}"
        return True, message, False
    except Exception as exc:
        print(f"[BODYQUEST] complete_current_day error: {exc}")
        return False, ACTIVITY_ERROR, False


def get_user_workout_history(user_id: int):
    return _progress_repo.get_user_workout_history(user_id)


def get_recent_workout_history(user_id: int, limit: int = 5):
    return _progress_repo.get_recent_workout_history(user_id, limit)
