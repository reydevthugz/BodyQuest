import flet as ft

from components.theme import ERROR_TEXT_COLOR, MUTED_TEXT_COLOR, PRIMARY_COLOR, TEXT_COLOR, feedback_text
from components.ui import glass_card, list_row, neon_button, soft_button
from pages.user.common import user_shell
from controllers.goal_controller import handle_start_plan
from services.plan_service import generate_plan_days, get_goal_duration
from services.session_service import get_current_user_id, get_session_value


def plan_preview_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        page.go("/login")
        return user_shell(
            page,
            "plan-preview",
            glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)),
            "Plan Preview",
        )
    selected_goal = get_session_value(page, "selected_goal", "")
    if not selected_goal:
        page.go("/user/goal-setup")
        return user_shell(
            page,
            "plan-preview",
            glass_card(
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("No selected goal found.", color=TEXT_COLOR, size=22, weight=ft.FontWeight.BOLD),
                        ft.Text("Please choose a goal first.", color=MUTED_TEXT_COLOR),
                    ],
                )
            ),
            "Plan Preview",
        )

    duration = get_goal_duration(selected_goal)
    sample_days = generate_plan_days(selected_goal, duration)[:7]
    feedback = feedback_text()

    def start_plan(_: ft.ControlEvent):
        result = handle_start_plan(page)
        if not result["success"]:
            feedback.value = result["message"] or ""
            feedback.color = ERROR_TEXT_COLOR
            page.update()
            return
        page.snack_bar = ft.SnackBar(ft.Text(result["message"] or "New Plan Activated!"))
        page.snack_bar.open = True
        page.go(result["data"]["route"])

    preview_rows = []
    for day in sample_days:
        preview_rows.append(
            list_row(
                ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text(f"Day {day['day_number']}: {day['title']}", color=TEXT_COLOR, weight=ft.FontWeight.W_600),
                        ft.Text(day["main_activity"], color=MUTED_TEXT_COLOR, size=12),
                    ],
                ),
            )
        )

    content = ft.Column(
        spacing=16,
        controls=[
            ft.Text("Plan Preview", size=30, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(f"Selected Goal: {selected_goal}", color=TEXT_COLOR, size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Recommended Duration: {duration} days", color=PRIMARY_COLOR),
                        ft.Text("Difficulty: Beginner", color=MUTED_TEXT_COLOR),
                        ft.Text("Estimated Daily Time: 20-35 minutes", color=MUTED_TEXT_COLOR),
                    ],
                )
            ),
            glass_card(ft.Column(spacing=10, controls=[ft.Text("First Week Preview", color=TEXT_COLOR, size=18)] + preview_rows)),
            ft.Row(
                spacing=10,
                controls=[
                    neon_button("Start Plan", ft.Icons.PLAY_ARROW, start_plan),
                    soft_button("Back", ft.Icons.ARROW_BACK, lambda _: page.go("/user/goal-setup")),
                ],
            ),
            feedback,
        ],
    )
    return user_shell(page, "plan-preview", content, "Plan Preview")
