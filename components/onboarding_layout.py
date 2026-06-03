"""Goal onboarding shell — no main app sidebar (Cyan & Black theme)."""
import flet as ft

from components.buttons import soft_button
from components.theme import (
    MUTED_TEXT_COLOR,
    PAGE_PADDING,
    PRIMARY_CYAN,
    TEXT_CYAN,
    TRANSPARENT,
    ambient_orbs,
    page_background,
    role_badge_style,
)
from controllers.auth_controller import handle_logout
from utils.auth_guard import require_user
from utils.messages import ACCESS_DENIED
from utils.navigation import go


def onboarding_shell(page: ft.Page, content: ft.Control, title: str = "BodyQuest") -> ft.View:
    if not require_user(page):
        return ft.View(
            route=page.route,
            controls=[ft.Text(ACCESS_DENIED, color=MUTED_TEXT_COLOR)],
        )

    def logout(_: ft.ControlEvent) -> None:
        result = handle_logout(page)
        go(page, result["data"]["route"])

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.FITNESS_CENTER, color=PRIMARY_CYAN, size=28),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text("BODYQUEST", color=TEXT_CYAN, weight=ft.FontWeight.BOLD, size=22),
                            ft.Text(title, color=MUTED_TEXT_COLOR, size=12),
                        ],
                    ),
                ],
            ),
            ft.Row(
                spacing=8,
                controls=[
                    ft.Container(
                        **role_badge_style(),
                        content=ft.Text("GOAL SETUP", color=PRIMARY_CYAN, size=10, weight=ft.FontWeight.BOLD),
                    ),
                    soft_button("Logout", ft.Icons.LOGOUT, logout),
                ],
            ),
        ],
    )

    return ft.View(
        route=page.route,
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(expand=True, gradient=page_background()),
                    *ambient_orbs(),
                    ft.SafeArea(
                        expand=True,
                        content=ft.Container(
                            expand=True,
                            padding=PAGE_PADDING,
                            content=ft.Column(
                                expand=True,
                                spacing=20,
                                controls=[
                                    header,
                                    ft.Container(
                                        expand=True,
                                        content=ft.Column(
                                            expand=True,
                                            scroll=ft.ScrollMode.AUTO,
                                            spacing=20,
                                            controls=[content],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ),
                ],
            )
        ],
    )
