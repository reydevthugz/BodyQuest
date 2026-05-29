"""Shared auth / public page shell (Cyan & Black theme)."""
import flet as ft

from components.cards import glass_card, status_badge
from components.theme import (
    MUTED_TEXT_COLOR,
    PAGE_PADDING,
    PRIMARY_CYAN,
    SECONDARY_COLOR,
    TEXT_CYAN,
    TRANSPARENT,
    ambient_orbs,
    brand_header,
    page_background,
    role_badge_style,
)


def auth_shell(page: ft.Page, title: str, subtitle: str, form: ft.Control, *, show_hero: bool = True) -> ft.View:
    show_preview = page.width >= 980 if page.width else True
    hero = None
    if show_hero:
        hero = ft.Container(
            visible=show_preview,
            col={"md": 6},
            content=glass_card(
                ft.Column(
                    spacing=18,
                    controls=[
                        brand_header(30),
                        ft.Text(
                            "Start small. Stay consistent. Unlock your fitness journey.",
                            size=32,
                            color=TEXT_CYAN,
                            weight=ft.FontWeight.W_700,
                        ),
                        ft.Text(
                            "A beginner fitness companion with cyan glass dashboards, daily unlocks, and achievements.",
                            size=14,
                            color=MUTED_TEXT_COLOR,
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                status_badge("Cyan UI", "cyan"),
                                status_badge("MySQL", "aqua"),
                            ],
                        ),
                    ],
                ),
                padding=28,
            ),
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
                            padding=PAGE_PADDING,
                            content=ft.ResponsiveRow(
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    hero or ft.Container(),
                                    ft.Container(
                                        col={"md": 6 if show_hero else 12},
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Container(
                                            width=470,
                                            content=ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                spacing=20,
                                                controls=[
                                                    brand_header(28),
                                                    ft.Container(
                                                        **role_badge_style(),
                                                        content=ft.Text("Public Access", color=PRIMARY_CYAN, size=10, weight=ft.FontWeight.BOLD),
                                                    ),
                                                    ft.Column(
                                                        spacing=6,
                                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                        controls=[
                                                            ft.Text(title, color=TEXT_CYAN, size=30, weight=ft.FontWeight.BOLD),
                                                            ft.Text(subtitle, color=MUTED_TEXT_COLOR, size=14),
                                                        ],
                                                    ),
                                                    glass_card(form, padding=24),
                                                    ft.Container(
                                                        border=ft.Border(top=ft.BorderSide(1, SECONDARY_COLOR), right=ft.BorderSide(0, TRANSPARENT), bottom=ft.BorderSide(0, TRANSPARENT), left=ft.BorderSide(0, TRANSPARENT)),
                                                        padding=ft.Padding(10, 8, 10, 8),
                                                        content=ft.Text("Secure, stylish and cyan-branded authentication pages.", color=MUTED_TEXT_COLOR, size=11),
                                                    ),
                                                ],
                                            ),
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
