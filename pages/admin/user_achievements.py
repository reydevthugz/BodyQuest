import flet as ft

from components.buttons import link_button, soft_button
from components.cards import glass_card, list_row
from components.theme import MUTED_TEXT_COLOR, TEXT_COLOR
from controllers.admin_controller import get_user_achievements_data
from services.session_service import get_session_value
from utils.auth_guard import require_admin
from utils.date_utils import format_datetime
from utils.messages import NO_ACHIEVEMENTS_ADMIN


def build_content(page: ft.Page) -> ft.Control:
    if not require_admin(page):
        return glass_card(ft.Text("You do not have permission to access this page.", color=MUTED_TEXT_COLOR))
    selected_user_id = get_session_value(page, "selected_user_id", None)
    if not selected_user_id:
        return glass_card(
            ft.Column(
                spacing=10,
                controls=[ft.Text("No user selected.", color=MUTED_TEXT_COLOR), link_button("Back to Users", lambda _: page.go("/admin/users"))],
            )
        )
    rows = get_user_achievements_data(page, int(selected_user_id))
    if not rows:
        body = ft.Text(NO_ACHIEVEMENTS_ADMIN, color=MUTED_TEXT_COLOR)
    else:
        body = ft.Column(
            spacing=8,
            controls=[
                list_row(
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(r["name"], color=TEXT_COLOR, weight=ft.FontWeight.W_600),
                            ft.Text(r.get("description") or "", color=MUTED_TEXT_COLOR, size=12),
                            ft.Text(f"Badge: {r.get('badge_type') or '-'} | Goal: {r.get('goal_type') or 'N/A'}", color=MUTED_TEXT_COLOR, size=11),
                            ft.Text(f"Earned: {format_datetime(r.get('earned_at'))}", color=MUTED_TEXT_COLOR, size=11),
                        ],
                    ),
                )
                for r in rows
            ],
        )
    return ft.Column(
        spacing=12,
        controls=[
            ft.Text("User Achievements", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(body),
            soft_button("Back to User Details", ft.Icons.ARROW_BACK, lambda _: page.go("/admin/users/details")),
        ],
    )


def user_achievements_view(page: ft.Page) -> ft.View:
    from components.admin_layout import admin_shell

    return admin_shell(page, "users/achievements", build_content(page))
