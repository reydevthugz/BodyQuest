import flet as ft

from components.theme import ERROR_TEXT_COLOR, MUTED_TEXT_COLOR, PRIMARY_COLOR, TEXT_COLOR, feedback_text
from components.ui import glass_card, neon_button, soft_button
from pages.user.common import user_shell
from utils.messages import NO_ACTIVE_PLAN
from services.plan_service import get_active_goal, get_current_unlocked_day, get_latest_completed_goal
from controllers.progress_controller import handle_complete_activity
from services.session_service import get_current_user_id


def activity_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        page.go("/login")
        return user_shell(page, "activity", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)), "Activity")

    goal = get_active_goal(user_id)
    if not goal:
        completed = get_latest_completed_goal(user_id)
        if completed:
            content = glass_card(
                ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("Goal Completed!", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"You finished your {completed['goal_type']} plan. Start a new goal anytime.",
                            color=MUTED_TEXT_COLOR,
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                neon_button("View Achievements", ft.Icons.MILITARY_TECH, lambda _: page.go("/user/achievements")),
                                soft_button("View History", ft.Icons.HISTORY, lambda _: page.go("/user/history")),
                                neon_button("Start New Plan", ft.Icons.TUNE, lambda _: page.go("/user/goal-setup")),
                            ],
                        ),
                    ],
                )
            )
            return user_shell(page, "activity", content, completed["goal_type"])
        content = glass_card(
            ft.Column(
                spacing=12,
                controls=[
                    ft.Text("No Active Plan", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Text(NO_ACTIVE_PLAN, color=MUTED_TEXT_COLOR),
                    neon_button("Choose Fitness Goal", ft.Icons.TUNE, lambda _: page.go("/user/goal-setup")),
                ],
            )
        )
        return user_shell(page, "activity", content, "No Active Plan")

    day = get_current_unlocked_day(goal["id"])
    if not day:
        content = glass_card(
            ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Goal completed! Great work.", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        spacing=10,
                        controls=[
                            neon_button("View Achievements", ft.Icons.MILITARY_TECH, lambda _: page.go("/user/achievements")),
                            soft_button("View History", ft.Icons.HISTORY, lambda _: page.go("/user/history")),
                        ],
                    ),
                ],
            )
        )
        return user_shell(page, "activity", content, goal["goal_type"])

    notice = feedback_text()

    def complete(_: ft.ControlEvent):
        result = handle_complete_activity(page, goal["id"], day["id"])
        notice.value = result["message"] or ""
        if result["success"]:
            page.snack_bar = ft.SnackBar(ft.Text(result["message"]))
            page.snack_bar.open = True
            page.go(result["data"]["route"])
        else:
            notice.color = ERROR_TEXT_COLOR
            page.update()

    content = ft.Column(
        spacing=16,
        controls=[
            ft.Text(f"Day {day['day_number']} Activity", size=30, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(day["title"], color=TEXT_COLOR, size=20, weight=ft.FontWeight.W_600),
                        ft.Text(f"Warm-up: {day['warmup']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Main Activity: {day['main_activity']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Cooldown: {day['cooldown']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Safety Tip: {day['safety_tip']}", color=PRIMARY_COLOR),
                        ft.Text(f"Estimated Minutes: {day['estimated_minutes']}", color=MUTED_TEXT_COLOR),
                    ],
                )
            ),
            neon_button("Mark as Completed", ft.Icons.CHECK_CIRCLE, complete),
            notice,
        ],
    )
    return user_shell(page, "activity", content, goal["goal_type"])
