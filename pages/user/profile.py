import flet as ft

from components.theme import MUTED_TEXT_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, TEXT_COLOR
from components.ui import glass_card, soft_button, stat_tile
from pages.user.common import show_change_plan_dialog, user_shell
from controllers.auth_controller import handle_logout
from controllers.user_controller import get_profile_summary
from services.session_service import get_current_user, get_current_user_id


def profile_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    user = get_current_user(page) or {}
    if not user_id:
        page.go("/login")
        return user_shell(page, "profile", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)), "Profile")

    summary = get_profile_summary(user_id)
    goal = summary["goal"]
    goal_name = goal["goal_type"] if goal else "No active plan"
    progress = summary["progress_percent"]
    achievement_count = summary["achievement_count"]
    workout_count = summary["workout_count"]

    content = ft.Column(
        spacing=16,
        controls=[
            glass_card(
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Profile", size=30, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Full Name: {user.get('full_name', '-')}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Email: {user.get('email', '-')}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Current Goal: {goal_name}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Progress Summary: {progress}%", color=SECONDARY_COLOR),
                    ],
                )
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(col={"sm": 6, "md": 4}, content=stat_tile("Achievements", str(achievement_count), ft.Icons.MILITARY_TECH, PRIMARY_COLOR)),
                    ft.Container(col={"sm": 6, "md": 4}, content=stat_tile("Completed Workouts", str(workout_count), ft.Icons.CHECK_CIRCLE, SECONDARY_COLOR)),
                ]
            ),
            ft.Row(
                spacing=10,
                controls=[
                    soft_button("Change Plan", ft.Icons.SYNC, lambda _: show_change_plan_dialog(page)),
                    soft_button(
                        "Logout",
                        ft.Icons.LOGOUT,
                        lambda _: page.go(handle_logout(page)["data"]["route"]),
                    ),
                ],
            ),
        ],
    )
    return user_shell(page, "profile", content, goal_name)
