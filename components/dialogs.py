import flet as ft

from components.buttons import link_button, soft_button
from components.theme import BORDER_CYAN, CARD, MUTED_TEXT_COLOR, TEXT_CYAN, glass_border
from controllers.goal_controller import handle_change_plan
from utils.messages import CHANGE_PLAN_CONFIRM
from utils.navigation import go


def _close_dialog(page: ft.Page, dialog: ft.AlertDialog) -> None:
    """Close dialog on Flet 0.85+ (no page.close)."""
    if hasattr(page, "pop_dialog"):
        page.pop_dialog()
    else:
        dialog.open = False
        page.update()


def show_change_plan_dialog(page: ft.Page) -> None:
    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=CARD,
        shape=ft.RoundedRectangleBorder(radius=16),
        title=ft.Text("Change Current Plan?", color=TEXT_CYAN, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            border=glass_border(1, BORDER_CYAN),
            border_radius=12,
            padding=12,
            content=ft.Text(CHANGE_PLAN_CONFIRM, color=MUTED_TEXT_COLOR),
        ),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close(_: ft.ControlEvent) -> None:
        _close_dialog(page, dialog)
        page.update()

    def proceed(_: ft.ControlEvent) -> None:
        result = handle_change_plan(page)
        _close_dialog(page, dialog)
        if result.get("success") and result.get("data"):
            go(page, result["data"]["route"])
            return
        page.snack_bar = ft.SnackBar(ft.Text(result.get("message") or "Unable to change plan."))
        page.snack_bar.open = True
        page.update()

    dialog.actions = [
        link_button("Cancel", close, muted=True),
        soft_button("Continue", ft.Icons.ARROW_FORWARD, proceed),
    ]

    if hasattr(page, "show_dialog"):
        page.show_dialog(dialog)
    elif hasattr(page, "open"):
        page.open(dialog)
    else:
        page.overlay.append(dialog)
        dialog.open = True
    page.update()
