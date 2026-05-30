import flet as ft

from components.cards import status_badge
from components.theme import MUTED_TEXT_COLOR, PRIMARY_COLOR, PROGRESS_TRACK, SECONDARY_COLOR, TEXT_COLOR
from components.ui import glass_card, neon_button, soft_button, stat_tile
from utils.messages import NO_ACTIVE_PLAN, NO_ACHIEVEMENTS, NO_WORKOUT_HISTORY
from pages.user.common import show_change_plan_dialog, user_shell
from controllers.progress_controller import get_dashboard_data
from services.achievement_service import get_recent_user_achievements
from services.progress_service import get_recent_workout_history
from services.session_service import get_current_user_id, get_current_user_name
from utils.date_utils import format_date


def dashboard_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    user_name = get_current_user_name(page) or "Athlete"
    if not user_id:
        page.go("/login")
        return user_shell(page, "dashboard", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)), "Dashboard")

    dash = get_dashboard_data(user_id)
    active_goal = dash.get("active_goal")
    if not active_goal:
        content = glass_card(
            ft.Column(
                spacing=14,
                controls=[
                    ft.Text("No Active Plan", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Text(NO_ACTIVE_PLAN, color=MUTED_TEXT_COLOR),
                    neon_button("Choose Fitness Goal", ft.Icons.TUNE, lambda _: page.go("/user/goal-setup")),
                ],
            )
        )
        return user_shell(page, "dashboard", content, "No Active Plan")

    goal_id = active_goal["id"]
    current_day = dash.get("current_day")
    completed = dash.get("completed", 0)
    total = int(active_goal["plan_duration"])
    remaining = max(total - completed, 0)
    percent = dash.get("percent", 0)
    recent_achievements = get_recent_user_achievements(user_id, 3)
    recent_history = get_recent_workout_history(user_id, 5)

    current_status = dash.get("current_day_status")
    status_controls = []
    if current_day and current_status:
        status_controls.append(status_badge(current_status.replace("_", " ").title(), "cyan" if current_status == "current" else "aqua"))

    top_card = glass_card(
        ft.Column(
            spacing=10,
            controls=[
                ft.Text(f"Welcome back, {user_name.split(' ')[0]}!", size=30, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                ft.Text(f"Current Goal: {active_goal['goal_type']} ({total} days)", color=MUTED_TEXT_COLOR),
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Text(
                            f"Today's Activity: Day {current_day['day_number']} - {current_day['title']}" if current_day else "All activities completed.",
                            color=SECONDARY_COLOR,
                        ),
                        *status_controls,
                    ],
                ),
                ft.ProgressBar(value=max(min(percent / 100, 1), 0), color=PRIMARY_COLOR, bgcolor=PROGRESS_TRACK, height=10),
                ft.Row(
                    spacing=12,
                    controls=[
                        neon_button("Continue Activity", ft.Icons.PLAY_CIRCLE_FILL_ROUNDED, lambda _: page.go("/user/activity")),
                        soft_button("Plan Timeline", ft.Icons.TIMELINE, lambda _: page.go("/user/timeline")),
                        soft_button("Change Plan", ft.Icons.SYNC, lambda _: show_change_plan_dialog(page)),
                    ],
                ),
            ],
        )
    )

    achievement_controls = (
        [ft.Text(NO_ACHIEVEMENTS, color=MUTED_TEXT_COLOR, size=12)]
        if not recent_achievements
        else [
            ft.Text(
                f"{item['name']} • {format_date(item.get('earned_at'))}",
                color=MUTED_TEXT_COLOR,
                size=12,
            )
            for item in recent_achievements
        ]
    )
    history_controls = (
        [ft.Text(NO_WORKOUT_HISTORY, color=MUTED_TEXT_COLOR, size=12)]
        if not recent_history
        else [
            ft.Text(
                f"Day {item['day_number']} {item['title']} • {format_date(item.get('completed_at'))}",
                color=MUTED_TEXT_COLOR,
                size=12,
            )
            for item in recent_history
        ]
    )

    content = ft.Column(
        spacing=16,
        controls=[
            top_card,
            ft.ResponsiveRow(
                run_spacing=12,
                controls=[
                    ft.Container(col={"sm": 6, "md": 4}, content=stat_tile("Completed", str(completed), ft.Icons.EMOJI_EVENTS, SECONDARY_COLOR)),
                    ft.Container(col={"sm": 6, "md": 4}, content=stat_tile("Remaining", str(remaining), ft.Icons.LOCAL_FIRE_DEPARTMENT, PRIMARY_COLOR)),
                    ft.Container(col={"sm": 6, "md": 4}, content=stat_tile("Progress", f"{percent}%", ft.Icons.TRENDING_UP, TEXT_COLOR)),
                ],
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"md": 6},
                        content=glass_card(ft.Column(spacing=8, controls=[ft.Text("Recent Achievements", color=TEXT_COLOR, size=18)] + achievement_controls)),
                    ),
                    ft.Container(
                        col={"md": 6},
                        content=glass_card(ft.Column(spacing=8, controls=[ft.Text("Recent Workout History", color=TEXT_COLOR, size=18)] + history_controls)),
                    ),
                ]
            ),
        ],
    )
    return user_shell(page, "dashboard", content, active_goal["goal_type"])
