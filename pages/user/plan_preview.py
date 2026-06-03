import flet as ft

from components.cards import status_badge
from components.theme import ERROR_TEXT_COLOR, MUTED_TEXT_COLOR, PRIMARY_COLOR, TEXT_COLOR, feedback_text
from components.ui import glass_card, list_row, neon_button, soft_button
from pages.user.common import onboarding_shell
from controllers.goal_controller import handle_start_plan
from services.plan_service import generate_plan_days, get_goal_duration
from services.session_service import get_current_user_id, get_session_value, set_session_value
from utils.navigation import go


def plan_preview_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        go(page, "/login")
        return onboarding_shell(
            page,
            glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)),
            "Plan Preview",
        )
    selected_goal = get_session_value(page, "selected_goal", "")
    if not selected_goal:
        go(page, "/user/goal-setup")
        return onboarding_shell(
            page,
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
    flash = str(get_session_value(page, "flash_message", "") or "").strip()
    if flash:
        feedback.value = flash
        feedback.color = PRIMARY_COLOR
        set_session_value(page, "flash_message", "")

    def start_plan(_: ft.ControlEvent):
        result = handle_start_plan(page)
        if not result["success"]:
            feedback.value = result["message"] or "Unable to start plan. Please try again."
            feedback.color = ERROR_TEXT_COLOR
            page.snack_bar = ft.SnackBar(ft.Text(feedback.value))
            page.snack_bar.open = True
            page.update()
            return
        route = (result.get("data") or {}).get("route") or "/user/dashboard"
        feedback.value = result["message"] or "Your BodyQuest plan is ready."
        feedback.color = PRIMARY_COLOR
        page.snack_bar = ft.SnackBar(ft.Text(feedback.value))
        page.snack_bar.open = True
        go(page, route)

    preview_rows = []
    for day in sample_days:
        minutes = int(day.get("estimated_minutes") or 20)
        day_num = int(day["day_number"])
        is_day_one = day_num == 1
        preview_status = "Current" if is_day_one else "Locked"
        preview_tone = "cyan" if is_day_one else "blue"
        if is_day_one:
            day_one_hint = soft_button("Use Start Plan above", ft.Icons.PLAY_ARROW, lambda _: None)
            day_one_hint.disabled = True
            action_col = ft.Column(
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    status_badge(preview_status, preview_tone),
                    day_one_hint,
                ],
            )
        else:
            locked_btn = soft_button("Locked", ft.Icons.LOCK_OUTLINE, lambda _: None)
            locked_btn.disabled = True
            action_col = ft.Column(
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    status_badge(preview_status, preview_tone),
                    locked_btn,
                ],
            )
        preview_rows.append(
            list_row(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=6,
                            expand=True,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            f"Day {day_num}: {day['title']}",
                                            color=TEXT_COLOR,
                                            weight=ft.FontWeight.W_600,
                                        ),
                                        status_badge(f"{minutes} MIN", "cyan"),
                                    ],
                                ),
                                ft.Text(day.get("description") or day["main_activity"], color=MUTED_TEXT_COLOR, size=12),
                                ft.Text(
                                    "Day 1 unlocks when you click Start Plan."
                                    if is_day_one
                                    else "Unlocks after you complete the previous day.",
                                    color=MUTED_TEXT_COLOR,
                                    size=11,
                                ),
                            ],
                        ),
                        action_col,
                    ],
                ),
            )
        )

    start_plan_btn = neon_button("Start Plan", ft.Icons.PLAY_ARROW, start_plan)
    back_route = (
        "/user/change-plan"
        if get_session_value(page, "changing_plan", False)
        else "/user/goal-setup"
    )
    back_btn = soft_button("Back", ft.Icons.ARROW_BACK, lambda _: go(page, back_route))

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
                        ft.Text(
                            "Click Start Plan to save your goal and activate Day 1 in MySQL.",
                            color=PRIMARY_COLOR,
                            size=12,
                        ),
                    ],
                )
            ),
            ft.Row(spacing=10, controls=[start_plan_btn, back_btn]),
            feedback,
            glass_card(
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text("First Week Preview", color=TEXT_COLOR, size=18, weight=ft.FontWeight.W_600),
                        ft.Text(
                            "Scroll to review your first week. Day 1 unlocks when you click Start Plan above.",
                            color=MUTED_TEXT_COLOR,
                            size=12,
                        ),
                        *preview_rows,
                    ],
                )
            ),
        ],
    )
    return onboarding_shell(page, content, "Plan Preview")
