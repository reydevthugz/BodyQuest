import flet as ft

from components.buttons import soft_button
from components.navigation import USER_NAV_ITEMS
from components.theme import (
    BORDER_SUBTLE,
    CARD_HOVER,
    GLOW_CYAN,
    MUTED_TEXT_COLOR,
    PAGE_PADDING,
    PRIMARY_CYAN,
    PROFILE_SURFACE,
    SIDEBAR_GRADIENT_USER,
    TEXT_CYAN,
    TRANSPARENT,
    ambient_orbs,
    glass_border,
    page_background,
    nav_item_style,
    role_badge_style,
)
from components.cards import glass_card
from controllers.auth_controller import handle_logout
from services.session_service import get_current_user_name
from utils.auth_guard import require_user
from utils.messages import ACCESS_DENIED


def user_page_layout(page: ft.Page, content: ft.Control, active_route: str, profile_subtitle: str = "Beginner Plan") -> ft.View:
    if not require_user(page):
        return ft.View(
            route=page.route,
            controls=[glass_card(ft.Text(ACCESS_DENIED, color=MUTED_TEXT_COLOR))],
        )
    section = active_route.removeprefix("/user/") if active_route.startswith("/user/") else "dashboard"
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
                        content=ft.Row(
                            expand=True,
                            spacing=0,
                            controls=[
                                _user_sidebar(page, section, profile_subtitle),
                                ft.Container(expand=True, padding=PAGE_PADDING, content=content),
                            ],
                        ),
                    ),
                ],
            )
        ],
    )


def user_shell(page: ft.Page, section: str, content: ft.Control, profile_subtitle: str = "Beginner Plan") -> ft.View:
    return user_page_layout(page, content, f"/user/{section}", profile_subtitle)


def _user_sidebar(page: ft.Page, section: str, profile_subtitle: str) -> ft.Container:
    items = []
    profile_name = get_current_user_name(page) or "User"
    for key, label, icon in USER_NAV_ITEMS:
        active = key == section
        styles = nav_item_style(active)
        items.append(
            ft.Container(
                border_radius=12,
                bgcolor=styles["bgcolor"],
                border=styles["border"],
                content=ft.TextButton(
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(icon, color=PRIMARY_CYAN if active else MUTED_TEXT_COLOR, size=18),
                            ft.Text(label, color=PRIMARY_CYAN if active else MUTED_TEXT_COLOR, size=13, weight=ft.FontWeight.W_500),
                        ],
                    ),
                    on_click=lambda _, k=key: page.go(f"/user/{k}"),
                ),
            )
        )

    def logout(_: ft.ControlEvent) -> None:
        result = handle_logout(page)
        page.go(result["data"]["route"])

    return ft.Container(
        width=260,
        padding=18,
        border=ft.Border(
            top=ft.BorderSide(0, TRANSPARENT),
            right=ft.BorderSide(1, BORDER_SUBTLE),
            bottom=ft.BorderSide(0, TRANSPARENT),
            left=ft.BorderSide(0, TRANSPARENT),
        ),
        gradient=ft.LinearGradient(colors=SIDEBAR_GRADIENT_USER),
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FITNESS_CENTER, color=PRIMARY_CYAN),
                        ft.Text("GYMBRO", color=TEXT_CYAN, weight=ft.FontWeight.BOLD, size=22),
                    ]
                ),
                ft.Container(
                    **role_badge_style(),
                    content=ft.Text("USER MODE", color=PRIMARY_CYAN, size=10, weight=ft.FontWeight.BOLD),
                ),
                ft.Column(spacing=6, controls=items, expand=True),
                ft.Container(
                    padding=12,
                    border_radius=14,
                    bgcolor=PROFILE_SURFACE,
                    border=glass_border(1, BORDER_SUBTLE),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=34,
                                height=34,
                                border_radius=17,
                                alignment=ft.Alignment(0, 0),
                                bgcolor=GLOW_CYAN,
                                content=ft.Icon(ft.Icons.PERSON, color=PRIMARY_CYAN, size=18),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(profile_name, color=TEXT_CYAN, size=13, weight=ft.FontWeight.W_600),
                                    ft.Text(profile_subtitle, color=MUTED_TEXT_COLOR, size=11),
                                ],
                            ),
                        ]
                    ),
                ),
                soft_button("Logout", ft.Icons.LOGOUT, logout),
            ],
            expand=True,
        ),
    )
