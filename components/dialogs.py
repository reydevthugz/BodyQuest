import flet as ft

from components.buttons import link_button
from components.theme import BORDER_CYAN, CARD, MUTED_TEXT_COLOR, TEXT_CYAN, glass_border
from controllers.goal_controller import handle_change_plan


def show_change_plan_dialog(page: ft.Page) -> None:
    def close(_: ft.ControlEvent) -> None:
        page.close(dialog)

    def proceed(_: ft.ControlEvent) -> None:
        page.close(dialog)
        result = handle_change_plan(page)
        if result.get("success") and result.get("data"):
            page.go(result["data"]["route"])

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=CARD,
        shape=ft.RoundedRectangleBorder(radius=16),
        title=ft.Text("Change Current Plan?", color=TEXT_CYAN, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            border=glass_border(1, BORDER_CYAN),
            border_radius=12,
            padding=12,
            content=ft.Text(
                "Changing your current plan will replace your active goal with a new beginner plan. "
                "Your previous progress was saved to history.",
                color=MUTED_TEXT_COLOR,
            ),
        ),
        actions=[
            link_button("Cancel", close, muted=True),
            link_button("Continue", proceed),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.open(dialog)
