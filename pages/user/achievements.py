import flet as ft

from components.theme import MUTED_TEXT_COLOR, PRIMARY_COLOR, TEXT_COLOR
from components.ui import glass_card, list_row
from pages.user.common import user_shell
from controllers.achievement_controller import get_user_achievements_data
from utils.messages import NO_ACHIEVEMENTS
from services.session_service import get_current_user_id
from utils.date_utils import format_date


def achievements_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        page.go("/login")
        return user_shell(page, "achievements", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)))

    items = get_user_achievements_data(user_id)
    if not items:
        content = glass_card(
            ft.Column(
                spacing=8,
                controls=[
                    ft.Text("My Achievements", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Text(NO_ACHIEVEMENTS, color=MUTED_TEXT_COLOR),
                ],
            )
        )
        return user_shell(page, "achievements", content)

    cards = []
    for item in items:
        cards.append(
            list_row(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.MILITARY_TECH, color=PRIMARY_COLOR, size=22),
                        ft.Column(
                            spacing=3,
                            controls=[
                                ft.Text(item["name"], color=TEXT_COLOR, weight=ft.FontWeight.W_600),
                                ft.Text(item.get("description") or "", color=MUTED_TEXT_COLOR, size=12),
                                ft.Text(
                                    f"Earned: {format_date(item.get('earned_at'))} • Goal: {item.get('goal_type') or 'N/A'}",
                                    color=MUTED_TEXT_COLOR,
                                    size=11,
                                ),
                            ],
                        ),
                    ],
                ),
            )
        )

    content = ft.Column(
        spacing=14,
        controls=[
            ft.Text("My Achievements", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(ft.Column(spacing=10, controls=cards)),
        ],
    )
    return user_shell(page, "achievements", content)
