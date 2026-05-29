import flet as ft

from components.theme import (
    BUTTON_RADIUS,
    BUTTON_TEXT_ON_PRIMARY,
    DANGER_BG,
    DANGER_BORDER,
    DANGER_TEXT,
    GLOW_CYAN,
    MUTED_CYAN,
    NEON_CYAN,
    PRIMARY_CYAN,
    TEXT_CYAN,
    BTN_SECONDARY_BG,
    BTN_SECONDARY_BG_HOVER,
    primary_button_style,
    secondary_button_style,
)


def primary_button(label: str, icon: str | None = None, on_click=None, width: int | None = None) -> ft.ElevatedButton:
    return neon_button(label, icon, on_click, width)


def neon_button(label: str, icon: str | None = None, on_click=None, width: int | None = None) -> ft.ElevatedButton:
    content = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True,
        spacing=8,
        controls=[
            ft.Icon(icon, size=18, color=BUTTON_TEXT_ON_PRIMARY) if icon else ft.Container(),
            ft.Text(label, color=BUTTON_TEXT_ON_PRIMARY),
        ],
    )
    return ft.ElevatedButton(
        content=content,
        on_click=on_click,
        width=width,
        style=primary_button_style(),
    )


def soft_button(label: str, icon: str | None = None, on_click=None) -> ft.OutlinedButton:
    return secondary_button(label, icon, on_click)


def secondary_button(label: str, icon: str | None = None, on_click=None) -> ft.OutlinedButton:
    content = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True,
        spacing=8,
        controls=[
            ft.Icon(icon, size=18, color=PRIMARY_CYAN) if icon else ft.Container(),
            ft.Text(label, color=TEXT_CYAN),
        ],
    )
    return ft.OutlinedButton(
        content=content,
        on_click=on_click,
        style=secondary_button_style(),
    )


def link_button(label: str, on_click=None, *, muted: bool = False) -> ft.TextButton:
    return ft.TextButton(
        label,
        on_click=on_click,
        style=ft.ButtonStyle(color=MUTED_CYAN if muted else PRIMARY_CYAN),
    )


def danger_button(label: str, icon: str | None = None, on_click=None) -> ft.OutlinedButton:
    content = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True,
        spacing=8,
        controls=[
            ft.Icon(icon, size=18, color=DANGER_TEXT) if icon else ft.Container(),
            ft.Text(label, color=DANGER_TEXT),
        ],
    )
    return ft.OutlinedButton(
        content=content,
        on_click=on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=BUTTON_RADIUS),
            side={ft.ControlState.DEFAULT: ft.BorderSide(1, DANGER_BORDER), ft.ControlState.HOVERED: ft.BorderSide(1, NEON_CYAN)},
            color={ft.ControlState.DEFAULT: DANGER_TEXT, ft.ControlState.HOVERED: NEON_CYAN},
            bgcolor={ft.ControlState.DEFAULT: DANGER_BG, ft.ControlState.HOVERED: f"{DANGER_BG}"},
            padding=ft.Padding(16, 13, 16, 13),
            text_style=ft.TextStyle(size=13, weight=ft.FontWeight.W_600),
        ),
    )
