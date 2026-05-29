import flet as ft

from components.buttons import link_button, soft_button
from components.cards import glass_card
from components.theme import MUTED_TEXT_COLOR, SECONDARY_COLOR, TEXT_COLOR
from controllers.admin_controller import get_user_details_data
from services.session_service import get_session_value
from utils.date_utils import format_date


def build_content(page: ft.Page) -> ft.Control:
    selected_user_id = get_session_value(page, "selected_user_id", None)
    if not selected_user_id:
        return glass_card(
            ft.Column(
                spacing=10,
                controls=[
                    ft.Text("No user selected.", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    link_button("Back to Users", lambda _: page.go("/admin/users")),
                ],
            )
        )
    details = get_user_details_data(page, int(selected_user_id))
    user = details.get("user")
    if not user:
        return glass_card(
            ft.Column(
                spacing=10,
                controls=[
                    ft.Text("User not found.", color=MUTED_TEXT_COLOR),
                    link_button("Back to Users", lambda _: page.go("/admin/users")),
                ],
            )
        )
    goal = details.get("goal")
    summary = details.get("summary") or {}
    achievements_total = details.get("achievements_total") or 0
    last = summary.get("last_completed_activity")
    last_text = (
        f"Day {last['day_number']} • {last['title']} ({format_date(last.get('completed_at'))})"
        if last
        else "No completed activity yet"
    )

    return ft.Column(
        spacing=12,
        controls=[
            ft.Text("User Details", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(f"Full name: {user['full_name']}", color=TEXT_COLOR),
                        ft.Text(f"Email: {user['email']}", color=MUTED_TEXT_COLOR),
                        ft.Text("Account role: User", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Current active goal: {(goal or {}).get('goal_type', 'No active goal')}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Current plan duration: {(goal or {}).get('plan_duration', 0)}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Current unlocked day: {summary.get('current_unlocked_day') or 'None'}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Completed days: {summary.get('completed_days', 0)}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Remaining days: {summary.get('remaining_days', 0)}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Progress: {summary.get('progress_percent', 0)}%", color=SECONDARY_COLOR),
                        ft.Text(f"Total achievements: {achievements_total}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Last completed activity: {last_text}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Account created: {format_date(user.get('created_at'))}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Current status: {str(summary.get('status', 'inactive')).title()}", color=MUTED_TEXT_COLOR),
                    ],
                )
            ),
            ft.Row(
                spacing=10,
                controls=[
                    soft_button("View User Achievements", ft.Icons.MILITARY_TECH, lambda _: page.go("/admin/users/achievements")),
                    soft_button("View User Workout History", ft.Icons.HISTORY, lambda _: page.go("/admin/users/history")),
                    soft_button("Back to Users", ft.Icons.ARROW_BACK, lambda _: page.go("/admin/users")),
                ],
            ),
        ],
    )


def user_details_view(page: ft.Page) -> ft.View:
    from components.admin_layout import admin_shell

    return admin_shell(page, "users/details", build_content(page))
