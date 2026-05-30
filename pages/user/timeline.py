import flet as ft

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
from controllers.progress_controller import handle_select_timeline_day
from pages.user.common import user_shell
from services.plan_service import get_active_goal
from services.progress_service import get_timeline_days, resolve_day_status
from services.session_service import get_current_user_id
from utils.messages import NO_ACTIVE_PLAN, TASK_LOCKED


def _status_tone(display_status: str) -> str:
    mapping = {
        "completed": "accent",
        "current": "cyan",
        "in_progress": "aqua",
        "locked": "blue",
    }
    return mapping.get(display_status, "cyan")


def _status_label(display_status: str) -> str:
    mapping = {
        "completed": "Completed",
        "current": "Current",
        "in_progress": "In Progress",
        "locked": "Locked",
    }
    return mapping.get(display_status, display_status.title())


def timeline_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        page.go("/login")
        return user_shell(page, "timeline", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)), "Timeline")

    goal = get_active_goal(user_id)
    if not goal:
        return user_shell(
            page,
            "timeline",
            glass_card(
                ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("No Active Plan", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                        ft.Text(NO_ACTIVE_PLAN, color=MUTED_TEXT_COLOR),
                        neon_button("Choose Fitness Goal", ft.Icons.TUNE, lambda _: page.go("/user/goal-setup")),
                    ],
                )
            ),
            "No Active Plan",
        )

    days = get_timeline_days(goal["id"])
    goal_id = goal["id"]

    def on_day_click(workout_day_id: int, display_status: str):
        def handler(_: ft.ControlEvent):
            if display_status == "locked":
                page.snack_bar = ft.SnackBar(ft.Text(TASK_LOCKED))
                page.snack_bar.open = True
                page.update()
                return
            result = handle_select_timeline_day(page, goal_id, workout_day_id)
            if not result["success"]:
                page.snack_bar = ft.SnackBar(ft.Text(result["message"] or TASK_LOCKED))
                page.snack_bar.open = True
                page.update()
                return
            page.go(result["data"]["route"])

        return handler

    rows = []
    for day in days:
        display_status = day.get("display_status") or resolve_day_status(day)
        completed = display_status == "completed"
        is_current = display_status in ("current", "in_progress")
        icon = ft.Icons.CHECK_CIRCLE if completed else (ft.Icons.PLAY_CIRCLE if is_current else ft.Icons.LOCK_OUTLINE)
        icon_color = ACCENT_COLOR if completed else (PRIMARY_COLOR if is_current else MUTED_TEXT_COLOR)
        bg = TIMELINE_COMPLETED_BG if completed else (TIMELINE_CURRENT_BG if is_current else TIMELINE_LOCKED_BG)
        minutes = int(day.get("estimated_minutes") or 0)
        rows.append(
            ft.Container(
                border_radius=12,
                bgcolor=bg,
                padding=12,
                ink=True,
                on_click=on_day_click(int(day["id"]), display_status),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(icon, color=icon_color, size=18),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(f"Day {day['day_number']}", color=TEXT_COLOR, size=13, weight=ft.FontWeight.W_600),
                                        ft.Text(day["title"], color=MUTED_TEXT_COLOR, size=12),
                                        ft.Text(f"{minutes} min", color=MUTED_TEXT_COLOR, size=11),
                                    ],
                                ),
                            ],
                        ),
                        status_badge(_status_label(display_status), _status_tone(display_status)),
                    ],
                ),
            )
        )

    content = ft.Column(
        spacing=16,
        controls=[
            ft.Text(f"Plan Timeline • {goal['goal_type']}", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            ft.Text("Tap the current task to open Today's Activity. Completed days can be viewed read-only.", color=MUTED_TEXT_COLOR, size=12),
            glass_card(ft.Column(spacing=10, controls=rows)),
        ],
    )
    return user_shell(page, "timeline", content, goal["goal_type"])
