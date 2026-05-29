import traceback

from pages.admin import admin_view
from pages.auth import landing_view, login_view, not_found_view, signup_view
from pages.auth.error import error_view
from pages.user import user_view
from services.plan_service import get_active_goal
from services.session_service import get_current_user_id, get_current_user_role, is_logged_in, set_session_value
from utils.route_utils import ADMIN_ROUTES, PUBLIC_ROUTES, USER_ROUTES, is_known_route, normalize_route

LANDING_ROUTES = {"/", "/landing"}
AUTH_ENTRY_ROUTES = LANDING_ROUTES | {"/login", "/signup"}


def route_guard(page, route: str) -> str:
    route = normalize_route(route)
    if not is_known_route(route):
        return "/404"

    if not is_logged_in(page):
        if route.startswith("/user") or route.startswith("/admin"):
            return "/login"
        return route

    role = get_current_user_role(page)

    if route in PUBLIC_ROUTES and route in AUTH_ENTRY_ROUTES:
        if role == "admin":
            return "/admin/dashboard"
        user_id = get_current_user_id(page)
        if user_id and not get_active_goal(user_id):
            return "/user/goal-setup"
        return "/user/dashboard"

    if route.startswith("/admin"):
        if role != "admin":
            set_session_value(page, "flash_message", "You do not have permission to access this page.")
            return "/user/dashboard"

    if route.startswith("/user"):
        if role == "admin":
            set_session_value(page, "flash_message", "You do not have permission to access this page.")
            return "/admin/dashboard"

    if role == "user" and route == "/user/dashboard":
        user_id = get_current_user_id(page)
        if user_id and not get_active_goal(user_id):
            return "/user/goal-setup"

    return route


def resolve_view(page, route: str):
    route = normalize_route(route)
    try:
        if route in LANDING_ROUTES:
            return landing_view(page)
        if route == "/login":
            return login_view(page)
        if route == "/signup":
            return signup_view(page)
        if route == "/404":
            return not_found_view(page)
        if route in USER_ROUTES:
            return user_view(page)
        if route in ADMIN_ROUTES:
            return admin_view(page)
        return not_found_view(page)
    except Exception as exc:
        print(f"[GYMBRO] resolve_view failed ({route}): {exc}")
        traceback.print_exc()
        return error_view(page, str(exc))
