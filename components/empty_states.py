import flet as ft

from components.cards import glass_card
from components.theme import MUTED_CYAN, PRIMARY_CYAN, TEXT_CYAN


def empty_state(title: str, message: str, action: ft.Control | None = None) -> ft.Control:
    controls: list[ft.Control] = [
        ft.Icon(ft.Icons.INBOX_OUTLINED, color=PRIMARY_CYAN, size=36),
        ft.Text(title, size=24, color=TEXT_CYAN, weight=ft.FontWeight.BOLD),
        ft.Text(message, color=MUTED_CYAN, size=13),
    ]
    if action is not None:
        controls.append(action)
    return glass_card(ft.Column(spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=controls))


def empty_state_message(message: str) -> ft.Text:
    return ft.Text(message, color=MUTED_CYAN, size=13)
