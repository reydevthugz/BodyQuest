from __future__ import annotations

import flet as ft

from requests import admin_request
from services import admin_service
from services.session_service import set_session_value
from utils.auth_guard import require_admin
from utils.messages import ACCESS_DENIED
from utils.response import error_response, success_response


def _admin_only(page: ft.Page) -> bool:
    return require_admin(page)


def get_dashboard_data() -> dict:
    return admin_service.get_dashboard_stats()


def get_users_data(page: ft.Page, search: str | None = None, status_filter: str | None = None):
    if not _admin_only(page):
        return []
    safe_search = admin_request.validate_user_search(search)
    safe_filter = admin_request.validate_status_filter(status_filter)
    return admin_service.get_all_users(safe_search, safe_filter)


def handle_view_user_details(page: ft.Page, user_id: int) -> dict:
    if not _admin_only(page):
        return error_response(ACCESS_DENIED)
    validation = admin_request.validate_user_id(user_id)
    if not validation["valid"]:
        return error_response(validation["errors"][0], validation["errors"])
    user = admin_service.get_user_details(int(user_id))
    if not user:
        return error_response("User not found.")
    set_session_value(page, "selected_user_id", int(user_id))
    return success_response("", {"route": "/admin/users/details"})


def _validated_target_user_id(user_id) -> int | None:
    validation = admin_request.validate_user_id(user_id)
    if not validation["valid"]:
        return None
    uid = int(user_id)
    if not admin_service.get_user_details(uid):
        return None
    return uid


def get_user_details_data(page: ft.Page, user_id: int) -> dict:
    if not _admin_only(page):
        return {"user": None}
    uid = _validated_target_user_id(user_id)
    if uid is None:
        return {"user": None}
    user = admin_service.get_user_details(uid)
    goal = admin_service.get_user_current_goal(uid)
    return {
        "user": user,
        "goal": goal,
        "summary": admin_service.get_user_progress_summary(uid),
        "achievements_total": len(admin_service.get_user_achievements(uid)),
    }


def get_user_achievements_data(page: ft.Page, user_id: int) -> list:
    if not _admin_only(page):
        return []
    uid = _validated_target_user_id(user_id)
    if uid is None:
        return []
    return admin_service.get_user_achievements(uid)


def get_user_history_data(page: ft.Page, user_id: int) -> list:
    if not _admin_only(page):
        return []
    uid = _validated_target_user_id(user_id)
    if uid is None:
        return []
    return admin_service.get_user_workout_history(uid)
