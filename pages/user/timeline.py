import flet as ft

from components.theme import (
    ACCENT_COLOR,
    MUTED_TEXT_COLOR,
    PRIMARY_COLOR,
    TIMELINE_COMPLETED_BG,
    TIMELINE_CURRENT_BG,
    TIMELINE_LOCKED_BG,
    TEXT_COLOR,
)
from components.buttons import link_button
from components.ui import glass_card, neon_button
from pages.user.common import user_shell
from services.plan_service import get_active_goal, get_current_unlocked_day, get_workout_days
from services.session_service import get_current_user_id
from utils.messages import NO_ACTIVE_PLAN


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

    days = get_workout_days(goal["id"])
    current = get_current_unlocked_day(goal["id"])
    current_num = int(current["day_number"]) if current else -1
    rows = []
    for day in days:
        completed = bool(day["is_completed"])
        unlocked = bool(day["is_unlocked"])
        is_current = unlocked and not completed and day["day_number"] == current_num
        icon = ft.Icons.CHECK_CIRCLE if completed else (ft.Icons.PLAY_CIRCLE if is_current else ft.Icons.LOCK_OUTLINE)
        icon_color = ACCENT_COLOR if completed else (PRIMARY_COLOR if is_current else MUTED_TEXT_COLOR)
        bg = TIMELINE_COMPLETED_BG if completed else (TIMELINE_CURRENT_BG if is_current else TIMELINE_LOCKED_BG)
        rows.append(
            ft.Container(
                border_radius=12,
                bgcolor=bg,
                padding=12,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(icon, color=icon_color, size=18),
                                ft.Column(
                                    spacing=1,
                                    controls=[
                                        ft.Text(f"Day {day['day_number']}", color=TEXT_COLOR, size=13),
                                        ft.Text(day["title"], color=MUTED_TEXT_COLOR, size=12),
                                    ],
                                ),
                            ],
                        ),
                        link_button("Open", lambda _: page.go("/user/activity")) if is_current else ft.Text("Locked", color=MUTED_TEXT_COLOR, size=12),
                    ],
                ),
            )
        )

    content = ft.Column(
        spacing=16,
        controls=[
            ft.Text(f"Plan Timeline • {goal['goal_type']}", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(ft.Column(spacing=10, controls=rows)),
        ],
    )
    return user_shell(page, "timeline", content, goal["goal_type"])
