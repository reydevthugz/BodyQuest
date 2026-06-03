import flet as ft

from components.cards import glass_card, list_row, status_badge
from components.theme import MUTED_TEXT_COLOR, TEXT_COLOR
from controllers.progress_controller import get_workout_history_data
from pages.user.common import user_shell
from utils.messages import NO_WORKOUT_HISTORY
from services.session_service import get_current_user_id
from utils.date_utils import format_date, format_datetime
from utils.navigation import go


def _status_label(status: str) -> str:
    if status == "active":
        return "Current Plan"
    if status == "completed":
        return "Completed Plan"
    if status == "replaced":
        return "Replaced Plan"
    return status.title()


def _plan_status_tone(status: str) -> str:
    if status == "active":
        return "cyan"
    if status == "completed":
        return "accent"
    return "blue"


def _format_duration(seconds: int | None) -> str:
    if not seconds:
        return ""
    minutes = max(int(seconds) // 60, 1)
    return f"Duration: {minutes} min"


def history_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        go(page, "/login")
        return user_shell(page, "history", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)))

    history = get_workout_history_data(user_id)["history"]
    if not history:
        content = glass_card(
            ft.Column(
                spacing=8,
                controls=[
                    ft.Text("Workout History", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Text(NO_WORKOUT_HISTORY, color=MUTED_TEXT_COLOR),
                ],
            )
        )
        return user_shell(page, "history", content)

    rows = []
    for item in history:
        completed_at = item.get("completed_at")
        date_text = format_date(completed_at)
        time_text = format_datetime(completed_at).split(" ")[-1] if completed_at else "-"
        duration_text = _format_duration(item.get("actual_duration_seconds"))
        plan_status = item.get("plan_status", "")
        rows.append(
            list_row(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(f"Day {item['day_number']} • {item['title']}", color=TEXT_COLOR, weight=ft.FontWeight.W_600),
                        ft.Text(f"Goal: {item['goal_type']}", color=MUTED_TEXT_COLOR, size=12),
                        ft.Text(f"Completed: {date_text} at {time_text}", color=MUTED_TEXT_COLOR, size=12),
                        ft.Text(duration_text, color=MUTED_TEXT_COLOR, size=12) if duration_text else ft.Container(),
                        status_badge(_status_label(plan_status), _plan_status_tone(plan_status)),
                    ],
                ),
            )
        )

    content = ft.Column(
        spacing=14,
        controls=[
            ft.Text("Workout History", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(ft.Column(spacing=10, controls=rows)),
        ],
    )
    return user_shell(page, "history", content)
