from __future__ import annotations

import flet as ft

from requests import goal_request
from services import plan_service
from services.session_service import get_current_user_id, get_session_value, is_user_session, set_session_value
from utils.auth_guard import require_user
from utils.messages import ACCESS_DENIED, PLAN_ERROR, PLAN_READY, SESSION_EXPIRED
from utils.response import error_response, success_response


def handle_goal_selection(page: ft.Page, goal_type: str) -> dict:
    if not require_user(page):
        return error_response(ACCESS_DENIED)
    validation = goal_request.validate_goal_selection(goal_type)
    if not validation["valid"]:
        return error_response(validation["errors"][0], validation["errors"])

    set_session_value(page, "selected_goal", validation["goal_type"])
    return success_response("Goal selected.", {"route": "/user/plan-preview"})


def handle_start_plan(page: ft.Page) -> dict:
    if not require_user(page):
        return error_response(ACCESS_DENIED)
    user_id = get_current_user_id(page)
    goal_type = get_session_value(page, "selected_goal", "")
    if not user_id:
        return error_response(SESSION_EXPIRED)
    validation = goal_request.validate_goal_selection(goal_type)
    if not validation["valid"]:
        return error_response(validation["errors"][0], validation["errors"])

    try:
        plan_service.start_new_plan(user_id, validation["goal_type"])
        set_session_value(page, "changing_plan", False)
        set_session_value(page, "selected_goal", "")
        return success_response(PLAN_READY, {"route": "/user/dashboard"})
    except Exception as exc:
        print(f"[GYMBRO] handle_start_plan error: {exc}")
        return error_response(PLAN_ERROR)


def handle_change_plan(page: ft.Page) -> dict:
    if not is_user_session(page):
        return error_response(ACCESS_DENIED)
    set_session_value(page, "changing_plan", True)
    return success_response("", {"route": "/user/change-plan"})
