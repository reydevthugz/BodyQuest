import flet as ft

from components.buttons import soft_button
from components.cards import glass_card, status_badge
from components.theme import (
    ACCENT_COLOR,
    MUTED_TEXT_COLOR,
    PRIMARY_COLOR,
    TIMELINE_COMPLETED_BG,
    TIMELINE_CURRENT_BG,
    TIMELINE_LOCKED_BG,
    TEXT_COLOR,
)
from components.ui import neon_button
from controllers.progress_controller import (
    handle_continue_timeline_task,
    handle_resume_timeline_task,
    handle_select_timeline_day,
    handle_start_timeline_task,
)
from pages.user.common import user_shell
from services.plan_service import get_active_goal
from services.progress_service import get_timeline_days, resolve_day_status
from services.session_service import get_current_user_id
from utils.messages import TASK_LOCKED, TASK_STARTED
from utils.navigation import go


def _status_tone(display_status: str) -> str:
    mapping = {
        "completed": "accent",
        "current": "cyan",
        "in_progress": "aqua",
        "stopped": "blue",
        "locked": "blue",
    }
    return mapping.get(display_status, "cyan")


def _status_label(display_status: str) -> str:
    mapping = {
        "completed": "Completed",
        "current": "Current",
        "in_progress": "In Progress",
        "stopped": "Stopped",
        "locked": "Locked",
    }
    return mapping.get(display_status, display_status.title())


def _show_snack(page: ft.Page, message: str) -> None:
    page.snack_bar = ft.SnackBar(ft.Text(message))
    page.snack_bar.open = True
    page.update()


def _navigate_activity(page: ft.Page, result: dict) -> None:
    if not result.get("success"):
        _show_snack(page, result.get("message") or TASK_LOCKED)
        return
    msg = result.get("message") or TASK_STARTED
    if msg:
        _show_snack(page, msg)
    route = (result.get("data") or {}).get("route") or "/user/activity"
    go(page, route)


def _task_action_button(page: ft.Page, goal_id: int, day_id: int, display_status: str):
    def make_start_handler(g_id: int, d_id: int):
        def _handler(_: ft.ControlEvent):
            result = handle_start_timeline_task(page, g_id, d_id)
            _navigate_activity(page, result)

        return _handler

    def make_continue_handler(g_id: int, d_id: int):
        def _handler(_: ft.ControlEvent):
            result = handle_continue_timeline_task(page, g_id, d_id)
            _navigate_activity(page, result)

        return _handler

    def make_resume_handler(g_id: int, d_id: int):
        def _handler(_: ft.ControlEvent):
            result = handle_resume_timeline_task(page, g_id, d_id)
            _navigate_activity(page, result)

        return _handler

    def make_view_completed_handler(g_id: int, d_id: int):
        def _handler(_: ft.ControlEvent):
            result = handle_select_timeline_day(page, g_id, d_id)
            if not result.get("success"):
                _show_snack(page, result.get("message") or TASK_LOCKED)
                return
            go(page, (result.get("data") or {}).get("route") or "/user/activity")

        return _handler

    if display_status == "completed":
        return soft_button("View Completed", ft.Icons.VISIBILITY, make_view_completed_handler(goal_id, day_id))
    if display_status == "in_progress":
        return neon_button("Continue Task", ft.Icons.PLAY_CIRCLE, make_continue_handler(goal_id, day_id))
    if display_status == "stopped":
        return neon_button("Resume Task", ft.Icons.PLAY_ARROW, make_resume_handler(goal_id, day_id))
    if display_status == "current":
        return neon_button("Start Task", ft.Icons.PLAY_ARROW, make_start_handler(goal_id, day_id))

    locked_btn = soft_button("Locked", ft.Icons.LOCK_OUTLINE, lambda _: None)
    locked_btn.disabled = True
    return locked_btn


def timeline_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        go(page, "/login")
        return user_shell(page, "timeline", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)), "Timeline")

    goal = get_active_goal(user_id)
    if not goal:
        go(page, "/user/goal-setup")
        return user_shell(
            page,
            "timeline",
            glass_card(ft.Text("Redirecting to goal selection...", color=MUTED_TEXT_COLOR)),
            "Timeline",
        )

    days = get_timeline_days(goal["id"])
    goal_id = int(goal["id"])

    rows = []
    for day in days:
        display_status = day.get("display_status") or resolve_day_status(day)
        completed = display_status == "completed"
        is_active = display_status in ("current", "in_progress", "stopped")
        icon = ft.Icons.CHECK_CIRCLE if completed else (ft.Icons.PLAY_CIRCLE if is_active else ft.Icons.LOCK_OUTLINE)
        icon_color = ACCENT_COLOR if completed else (PRIMARY_COLOR if is_active else MUTED_TEXT_COLOR)
        bg = TIMELINE_COMPLETED_BG if completed else (TIMELINE_CURRENT_BG if is_active else TIMELINE_LOCKED_BG)
        minutes = int(day.get("estimated_minutes") or 0)
        day_id = int(day["id"])
        action_btn = _task_action_button(page, goal_id, day_id, display_status)

        rows.append(
            ft.Container(
                border_radius=12,
                bgcolor=bg,
                padding=12,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(icon, color=icon_color, size=18),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(f"Day {day['day_number']}", color=TEXT_COLOR, size=13, weight=ft.FontWeight.W_600),
                                        ft.Text(day["title"], color=TEXT_COLOR, size=12, weight=ft.FontWeight.W_500),
                                        ft.Text(day.get("description") or day.get("main_activity") or "", color=MUTED_TEXT_COLOR, size=11),
                                        ft.Text(f"{minutes} min", color=MUTED_TEXT_COLOR, size=11),
                                    ],
                                ),
                            ],
                        ),
                        ft.Column(
                            spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                status_badge(_status_label(display_status), _status_tone(display_status)),
                                action_btn,
                            ],
                        ),
                    ],
                ),
            )
        )

    content = ft.Column(
        spacing=16,
        controls=[
            ft.Text(f"Plan Timeline • {goal['goal_type']}", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Start, continue, or resume the current day to open Today's Activity. Complete each day in order to unlock the next.",
                color=MUTED_TEXT_COLOR,
                size=12,
            ),
            glass_card(ft.Column(spacing=10, controls=rows if rows else [ft.Text("No tasks found. Start your plan first.", color=MUTED_TEXT_COLOR)])),
        ],
    )
    return user_shell(page, "timeline", content, goal["goal_type"])
