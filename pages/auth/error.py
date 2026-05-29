import flet as ft

from components.auth_layout import auth_shell
from components.buttons import neon_button
from components.theme import MUTED_TEXT_COLOR


def error_view(page: ft.Page, message: str) -> ft.View:
    return auth_shell(
        page,
        "Something went wrong",
        "An unexpected error occurred while loading this page.",
        ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    message or "Unknown error",
                    color=MUTED_TEXT_COLOR,
                    size=13,
                    selectable=True,
                ),
                neon_button("Back to Login", ft.Icons.LOGIN, lambda _: page.go("/login"), width=420),
            ],
        ),
        show_hero=False,
    )
