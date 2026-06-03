import flet as ft

from components.theme import MUTED_TEXT_COLOR, PRIMARY_COLOR, TEXT_COLOR
from components.ui import glass_card, goal_card, neon_button
from pages.user.common import onboarding_shell
from controllers.goal_controller import handle_goal_selection
from models.goal_model import GOAL_DURATIONS, GOAL_DESCRIPTIONS
from services.session_service import get_current_user_id, get_session_value, set_session_value
from utils.navigation import go


def goal_setup_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    title = "Change Plan" if page.route == "/user/change-plan" else "Goal Selection"
    if not user_id:
        go(page, "/login")
        return onboarding_shell(
            page,
            glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)),
            title,
        )

    def select_goal(goal: str):
        def _handler(_: ft.ControlEvent):
            result = handle_goal_selection(page, goal)
            if result["success"]:
                go(page, result["data"]["route"])

        return _handler

    cards = []
    for goal, duration in GOAL_DURATIONS.items():
        cards.append(
            ft.Container(
                col={"sm": 12, "md": 6, "lg": 4},
                content=goal_card(
                    ft.Column(
                        spacing=12,
                        controls=[
                            ft.Text(goal, size=21, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                            ft.Text(GOAL_DESCRIPTIONS.get(goal, ""), color=MUTED_TEXT_COLOR, size=12),
                            ft.Text(f"Recommended Duration: {duration} days", color=PRIMARY_COLOR, size=12),
                            neon_button("Select", ft.Icons.CHECK_CIRCLE, select_goal(goal)),
                        ],
                    ),
                ),
            )
        )

    flash = str(get_session_value(page, "flash_message", "") or "").strip()
    intro_controls = [
        ft.Text("Choose Your Fitness Goal", size=30, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
        ft.Text("Select one goal to generate your beginner daily plan.", color=MUTED_TEXT_COLOR),
    ]
    if flash:
        intro_controls.append(ft.Text(flash, color=PRIMARY_COLOR, size=12))
        set_session_value(page, "flash_message", "")

    content = ft.Column(
        spacing=16,
        controls=[
            *intro_controls,
            ft.ResponsiveRow(run_spacing=12, controls=cards),
        ],
    )
    return onboarding_shell(page, content, title)
