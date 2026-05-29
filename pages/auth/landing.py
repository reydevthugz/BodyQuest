import flet as ft

from components.buttons import neon_button, secondary_button
from components.cards import accent_mini_card, glass_card, progress_card, status_badge
from components.theme import (
    MUTED_TEXT_COLOR,
    PAGE_PADDING,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
    ambient_orbs,
    brand_header,
    page_background,
)


def _preview_dashboard() -> ft.Control:
    return glass_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Fitness Dashboard", color=TEXT_COLOR, size=16, weight=ft.FontWeight.W_600),
                        status_badge("Live Preview", "cyan"),
                    ],
                ),
                progress_card("Plan Progress", 0.42),
                ft.Row(
                    spacing=10,
                    controls=[
                        accent_mini_card(
                            ft.Icons.DIRECTIONS_RUN,
                            "Day 5",
                            "Today's Activity",
                            accent=PRIMARY_COLOR,
                        ),
                        accent_mini_card(
                            ft.Icons.MILITARY_TECH,
                            "7",
                            "Achievements",
                            accent=SECONDARY_COLOR,
                        ),
                    ],
                ),
            ],
        ),
        padding=22,
    )


def landing_view(page: ft.Page) -> ft.View:
    return ft.View(
        route=page.route if page.route in ("/", "/landing") else "/",
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(expand=True, gradient=page_background()),
                    *ambient_orbs(),
                    ft.SafeArea(
                        expand=True,
                        content=ft.Container(
                            padding=PAGE_PADDING,
                            content=ft.ResponsiveRow(
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        col={"md": 6},
                                        content=ft.Column(
                                            spacing=22,
                                            controls=[
                                                brand_header(34),
                                                ft.Text(
                                                    "Start small. Stay consistent. Unlock your fitness journey.",
                                                    size=38,
                                                    color=TEXT_COLOR,
                                                    weight=ft.FontWeight.W_700,
                                                ),
                                                ft.Text(
                                                    "GymBro helps beginners choose a fitness goal, follow a structured daily plan, "
                                                    "unlock activities one day at a time, and earn achievements — with a separate admin "
                                                    "dashboard for real-time monitoring.",
                                                    size=15,
                                                    color=MUTED_TEXT_COLOR,
                                                ),
                                                ft.Row(
                                                    spacing=12,
                                                    controls=[
                                                        neon_button(
                                                            "Get Started",
                                                            ft.Icons.ROCKET_LAUNCH,
                                                            lambda _: page.go("/signup"),
                                                        ),
                                                        secondary_button(
                                                            "Login",
                                                            ft.Icons.LOGIN,
                                                            lambda _: page.go("/login"),
                                                        ),
                                                    ],
                                                ),
                                                ft.Row(
                                                    spacing=10,
                                                    controls=[
                                                        status_badge("User Mode", "cyan"),
                                                        status_badge("Admin Mode", "aqua"),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ),
                                    ft.Container(col={"md": 6}, content=_preview_dashboard()),
                                ],
                            ),
                        ),
                    ),
                ],
            )
        ],
    )
