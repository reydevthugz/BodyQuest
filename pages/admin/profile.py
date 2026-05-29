import flet as ft

from components.buttons import soft_button
from components.cards import glass_card
from components.theme import MUTED_TEXT_COLOR, TEXT_COLOR
from controllers.auth_controller import handle_logout
from services.session_service import get_current_user


def build_content(page: ft.Page) -> ft.Control:
    user = get_current_user(page) or {}
    return ft.Column(
        spacing=12,
        controls=[
            ft.Text("Admin Profile", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(f"Full name: {user.get('full_name', 'System Admin')}", color=TEXT_COLOR),
                        ft.Text(f"Email: {user.get('email', '-')}", color=MUTED_TEXT_COLOR),
                        ft.Text("Role: System Administrator", color=MUTED_TEXT_COLOR),
                    ],
                )
            ),
            soft_button("Logout", ft.Icons.LOGOUT, lambda _: page.go(handle_logout(page)["data"]["route"])),
        ],
    )


def profile_view(page: ft.Page) -> ft.View:
    from components.admin_layout import admin_shell

    return admin_shell(page, "profile", build_content(page))
