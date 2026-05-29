import flet as ft

from components.cards import glass_card
from components.theme import MUTED_TEXT_COLOR
from pages.admin.all_achievements import all_achievements_view
from pages.admin.dashboard import dashboard_view
from pages.admin.leaderboard import leaderboard_view
from pages.admin.profile import profile_view
from pages.admin.reports import reports_view
from pages.admin.user_achievements import user_achievements_view
from pages.admin.user_details import user_details_view
from pages.admin.user_history import user_history_view
from pages.admin.users import users_view
from services.session_service import is_admin_session


def admin_view(page: ft.Page) -> ft.View:
    if not is_admin_session(page):
        from pages.auth.login import login_view

        return login_view(page)
    route = page.route
    if route == "/admin/dashboard":
        return dashboard_view(page)
    if route == "/admin/users":
        return users_view(page)
    if route == "/admin/users/details":
        return user_details_view(page)
    if route == "/admin/users/achievements":
        return user_achievements_view(page)
    if route == "/admin/users/history":
        return user_history_view(page)
    if route == "/admin/achievements":
        return all_achievements_view(page)
    if route == "/admin/leaderboard":
        return leaderboard_view(page)
    if route == "/admin/reports":
        return reports_view(page)
    if route == "/admin/profile":
        return profile_view(page)

    section = route.removeprefix("/admin/") if route.startswith("/admin/") else "dashboard"
    from components.admin_layout import admin_shell

    return admin_shell(page, section, glass_card(ft.Text("Admin page not found.", color=MUTED_TEXT_COLOR)))


__all__ = [
    "admin_view",
    "dashboard_view",
    "users_view",
    "user_details_view",
    "user_achievements_view",
    "user_history_view",
    "all_achievements_view",
    "leaderboard_view",
    "reports_view",
    "profile_view",
]
