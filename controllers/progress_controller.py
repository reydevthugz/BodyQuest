from __future__ import annotations

import flet as ft

from requests import progress_request
from services import plan_service, progress_service
from services.session_service import get_current_user_id
from utils.auth_guard import require_user
from utils.messages import ACCESS_DENIED, SESSION_EXPIRED
from utils.response import error_response, success_response


def handle_complete_activity(page: ft.Page, goal_id: int, workout_day_id: int) -> dict:
    if not require_user(page):
        return error_response(ACCESS_DENIED)
    user_id = get_current_user_id(page)
    validation = progress_request.validate_complete_activity(user_id, goal_id, workout_day_id)
    if not validation["valid"]:
        return error_response(validation["errors"][0], validation["errors"])
    if not user_id:
        return error_response(SESSION_EXPIRED)

    ok, message, finished = progress_service.complete_current_day(user_id, goal_id, workout_day_id)
    if not ok:
        return error_response(message)
    route = "/user/achievements" if finished else "/user/dashboard"
    return success_response(message, {"finished": finished, "route": route})


def get_dashboard_data(user_id: int) -> dict:
    active_goal = plan_service.get_active_goal(user_id)
    if not active_goal:
        return {"active_goal": None}
    goal_id = active_goal["id"]
    return {
        "active_goal": active_goal,
        "current_day": plan_service.get_current_unlocked_day(goal_id),
        "completed": plan_service.get_completed_days_count(goal_id),
        "percent": plan_service.get_progress_percentage(goal_id),
    }
