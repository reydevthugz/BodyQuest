import flet as ft

from components.theme import (
    ACCENT_COLOR,
    BORDER_CYAN,
    CARD,
    CARD_HOVER,
    CARD_RADIUS,
    CARD_SHADOW,
    GLASS_BG,
    GLASS_GRADIENT_START,
    GOAL_CARD_BG,
    GLOW_CYAN,
    GLOW_AQUA,
    LIST_ROW_BORDER,
    MUTED_TEXT_COLOR,
    PRIMARY_CYAN,
    PROGRESS_TRACK,
    SECONDARY_COLOR,
    SURFACE,
    TEXT_CYAN,
    accent_surface,
    glass_border,
)


def glass_card(content: ft.Control, expand: bool = False, padding: int = 20) -> ft.Container:
    return ft.Container(
        content=content,
        expand=expand,
        padding=padding,
        bgcolor=GLASS_BG,
        border=glass_border(1, BORDER_CYAN),
        border_radius=CARD_RADIUS,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[GLASS_GRADIENT_START, CARD, CARD_HOVER],
        ),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=32,
            color=CARD_SHADOW,
            offset=ft.Offset(0, 14),
        ),
    )


def list_row(content: ft.Control, padding: int = 12) -> ft.Container:
    return ft.Container(
        padding=padding,
        border_radius=12,
        bgcolor=SURFACE,
        border=glass_border(1, LIST_ROW_BORDER),
        content=content,
    )


def accent_mini_card(
    icon: str,
    title: str,
    subtitle: str,
    *,
    accent: str = PRIMARY_CYAN,
) -> ft.Container:
    bg, border = accent_surface(accent)
    return ft.Container(
        expand=True,
        padding=14,
        border_radius=14,
        bgcolor=bg,
        border=border,
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Icon(icon, color=accent, size=20),
                ft.Text(title, color=TEXT_CYAN, size=13, weight=ft.FontWeight.W_600),
                ft.Text(subtitle, color=MUTED_TEXT_COLOR, size=11),
            ],
        ),
    )


def stat_tile(title: str, value: str, icon: str, color: str) -> ft.Container:
    return glass_card(
        ft.Column(
            controls=[
                ft.Icon(icon, color=color, size=22),
                ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=TEXT_CYAN),
                ft.Text(title, size=11, color=MUTED_TEXT_COLOR),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=16,
    )


def stat_card(title: str, value: str, icon: str, color: str) -> ft.Container:
    return stat_tile(title, value, icon, color)


def status_badge(text: str, tone: str = "cyan") -> ft.Container:
    palette = {
        "cyan": (PRIMARY_CYAN, GLOW_CYAN),
        "primary": (PRIMARY_CYAN, GLOW_CYAN),
        "aqua": (SECONDARY_COLOR, GLOW_AQUA),
        "blue": (SECONDARY_COLOR, GLOW_AQUA),
        "accent": (ACCENT_COLOR, f"{ACCENT_COLOR}22"),
    }
    color, bg = palette.get(tone, palette["cyan"])
    return ft.Container(
        padding=ft.Padding(10, 4, 10, 4),
        border_radius=999,
        bgcolor=bg,
        border=glass_border(1, f"{color}44"),
        content=ft.Text(text.upper(), size=10, color=color, weight=ft.FontWeight.W_700),
    )


def progress_card(label: str, value: float) -> ft.Column:
    return ft.Column(
        spacing=5,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[ft.Text(label, color=TEXT_CYAN), ft.Text(f"{int(value * 100)}%", color=MUTED_TEXT_COLOR)],
            ),
            ft.ProgressBar(value=value, color=PRIMARY_CYAN, bgcolor=PROGRESS_TRACK, height=9, border_radius=8),
        ],
    )


def goal_card(content: ft.Control) -> ft.Container:
    return ft.Container(
        content=content,
        padding=18,
        border_radius=CARD_RADIUS,
        bgcolor=GOAL_CARD_BG,
        border=glass_border(1, BORDER_CYAN),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=22, color=GLOW_CYAN, offset=ft.Offset(0, 6)),
    )
