import flet as ft

from components.buttons import soft_button
from components.navigation import ADMIN_NAV_ITEMS
from components.theme import (
    BORDER_SUBTLE,
    CARD_HOVER,
    GLOW_CYAN,
    MUTED_TEXT_COLOR,
    PAGE_PADDING,
    PRIMARY_CYAN,
    PROFILE_SURFACE,
    SECONDARY_COLOR,
    SIDEBAR_GRADIENT_ADMIN,
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
from utils.auth_guard import require_admin
from utils.messages import ACCESS_DENIED


def admin_page_layout(page: ft.Page, content: ft.Control, active_section: str) -> ft.View:
    if not require_admin(page):
        return ft.View(
            route=page.route,
            controls=[glass_card(ft.Text(ACCESS_DENIED, color=MUTED_TEXT_COLOR))],
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
                        content=ft.Row(
                            expand=True,
                            spacing=0,
                            controls=[
                                _admin_sidebar(page, active_section),
                                ft.Container(expand=True, padding=PAGE_PADDING, content=content),
                            ],
                        ),
                    ),
                ],
            )
        ],
    )


def admin_shell(page: ft.Page, section: str, content: ft.Control) -> ft.View:
    return admin_page_layout(page, content, section)


def _admin_sidebar(page: ft.Page, section: str) -> ft.Container:
    rows = []
    for key, label, icon in ADMIN_NAV_ITEMS:
        active = key == section
        styles = nav_item_style(active)
        rows.append(
            ft.Container(
                border_radius=12,
                bgcolor=styles["bgcolor"],
                border=styles["border"],
                content=ft.TextButton(
                    on_click=lambda _, k=key: page.go(f"/admin/{k}"),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(icon, color=PRIMARY_CYAN if active else MUTED_TEXT_COLOR, size=18),
                            ft.Text(label, color=PRIMARY_CYAN if active else MUTED_TEXT_COLOR, size=13, weight=ft.FontWeight.W_500),
                        ],
                    ),
                ),
            )
        )

    def logout(_: ft.ControlEvent) -> None:
        page.go(handle_logout(page)["data"]["route"])

    admin_name = get_current_user_name(page) or "Admin"

    return ft.Container(
        width=280,
        padding=18,
        border=ft.Border(
            top=ft.BorderSide(0, TRANSPARENT),
            right=ft.BorderSide(1, BORDER_SUBTLE),
            bottom=ft.BorderSide(0, TRANSPARENT),
            left=ft.BorderSide(0, TRANSPARENT),
        ),
        gradient=ft.LinearGradient(colors=SIDEBAR_GRADIENT_ADMIN),
        content=ft.Column(
            expand=True,
            spacing=16,
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FITNESS_CENTER, color=PRIMARY_CYAN),
                        ft.Text("GYMBRO", color=TEXT_CYAN, size=22, weight=ft.FontWeight.BOLD),
                    ]
                ),
                ft.Container(
                    **role_badge_style(),
                    content=ft.Text("ADMIN MODE", color=PRIMARY_CYAN, size=10, weight=ft.FontWeight.BOLD),
                ),
                ft.Column(spacing=6, controls=rows, expand=True),
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
                                content=ft.Icon(ft.Icons.SHIELD, color=PRIMARY_CYAN, size=18),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(admin_name, color=TEXT_CYAN, size=13, weight=ft.FontWeight.W_600),
                                    ft.Text("System Monitoring", color=MUTED_TEXT_COLOR, size=11),
                                ],
                            ),
                        ]
                    ),
                ),
                soft_button("Logout", ft.Icons.LOGOUT, logout),
            ],
        ),
    )
