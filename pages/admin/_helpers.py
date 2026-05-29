import flet as ft

from components.theme import (
    GLOW_CYAN,
    LIST_ROW_BORDER,
    MUTED_TEXT_COLOR,
    PRIMARY_COLOR,
    PROGRESS_TRACK,
    SECONDARY_COLOR,
    SURFACE_ROW,
    TEXT_COLOR,
    glass_border,
)


def progress_row(label: str, value: float) -> ft.Column:
    return ft.Column(
        spacing=5,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[ft.Text(label, color=TEXT_COLOR), ft.Text(f"{int(value * 100)}%", color=MUTED_TEXT_COLOR)],
            ),
            ft.ProgressBar(value=value, color=PRIMARY_COLOR, bgcolor=PROGRESS_TRACK, height=9, border_radius=8),
        ],
    )


def achievement_row(title: str, subtitle: str) -> ft.Container:
    return ft.Container(
        padding=12,
        border_radius=12,
        bgcolor=SURFACE_ROW,
        border=glass_border(1, LIST_ROW_BORDER),
        content=ft.Row(
            controls=[
                ft.Container(
                    width=34,
                    height=34,
                    border_radius=17,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=GLOW_CYAN,
                    content=ft.Icon(ft.Icons.MILITARY_TECH, size=18, color=PRIMARY_COLOR),
                ),
                ft.Column(
                    spacing=1,
                    controls=[ft.Text(title, color=TEXT_COLOR, size=13), ft.Text(subtitle, color=MUTED_TEXT_COLOR, size=12)],
                ),
            ]
        ),
    )


def leader_row(rank: str, name: str, goal: str, progress: float, badges: str) -> ft.Container:
    return ft.Container(
        padding=10,
        border_radius=12,
        bgcolor=SURFACE_ROW,
        border=glass_border(1, LIST_ROW_BORDER),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=14,
                    controls=[
                        ft.Text(rank, color=SECONDARY_COLOR, size=16, weight=ft.FontWeight.W_700),
                        ft.Column(spacing=1, controls=[ft.Text(name, color=TEXT_COLOR, size=14), ft.Text(goal, color=MUTED_TEXT_COLOR, size=12)]),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=120,
                            content=ft.ProgressBar(value=progress, color=PRIMARY_COLOR, bgcolor=PROGRESS_TRACK, height=8),
                        ),
                        ft.Text(f"{int(progress * 100)}%", color=MUTED_TEXT_COLOR, size=12),
                        ft.Text(badges, color=SECONDARY_COLOR, size=14, weight=ft.FontWeight.W_600),
                    ],
                ),
            ],
        ),
    )
