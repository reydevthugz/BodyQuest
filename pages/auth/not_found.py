import flet as ft

from components.auth_layout import auth_shell
from components.buttons import neon_button, secondary_button
from components.theme import MUTED_TEXT_COLOR


def not_found_view(page: ft.Page) -> ft.View:
    return auth_shell(
        page,
        "404 — Page Not Found",
        "The route does not exist.",
        ft.Column(
            spacing=16,
            controls=[
                ft.Text("This page could not be found.", color=MUTED_TEXT_COLOR, size=13),
                neon_button("Back to Home", ft.Icons.HOME, lambda _: page.go("/"), width=420),
                secondary_button("Login", ft.Icons.LOGIN, lambda _: page.go("/login")),
            ],
        ),
        show_hero=False,
    )
