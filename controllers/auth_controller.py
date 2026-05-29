from __future__ import annotations

import flet as ft

from requests import auth_request
from services import auth_service, plan_service
from services.session_service import clear_current_user, set_current_user
from utils.messages import GENERIC_ERROR, LOGIN_INVALID, SESSION_EXPIRED, SIGNUP_SUCCESS
from utils.response import error_response, success_response


def handle_login(page: ft.Page, email: str, password: str) -> dict:
    validation = auth_request.validate_login(email, password)
    if not validation["valid"]:
        return error_response(validation["errors"][0], validation["errors"])

    try:
        user = auth_service.login_user(validation["email"], password)
    except Exception as exc:
        print(f"[GYMBRO] handle_login error: {exc}")
        return error_response(LOGIN_INVALID)

    if not user:
        return error_response(LOGIN_INVALID)

    set_current_user(page, user)
    if user["role"] == "admin":
        route = "/admin/dashboard"
    elif plan_service.get_active_goal(user["id"]):
        route = "/user/dashboard"
    else:
        route = "/user/goal-setup"
    return success_response("Login successful.", {"user": user, "route": route})


def handle_signup(page: ft.Page, full_name: str, email: str, password: str, confirm_password: str) -> dict:
    validation = auth_request.validate_signup(full_name, email, password, confirm_password)
    if not validation["valid"]:
        return error_response(validation["errors"][0], validation["errors"])

    ok, message = auth_service.create_user(
        validation["full_name"],
        validation["email"],
        validation["password"],
        role="user",
    )
    if not ok:
        return error_response(message)

    try:
        user = auth_service.login_user(validation["email"], validation["password"])
    except Exception as exc:
        print(f"[GYMBRO] handle_signup login error: {exc}")
        return error_response(GENERIC_ERROR)

    if not user:
        return error_response(LOGIN_INVALID)

    set_current_user(page, user)
    return success_response(SIGNUP_SUCCESS, {"user": user, "route": "/user/goal-setup"})


def handle_logout(page: ft.Page) -> dict:
    clear_current_user(page)
    return success_response("Logged out.", {"route": "/login"})
