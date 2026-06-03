import traceback

import flet as ft

from config.settings import APP_NAME
from components.theme import BACKGROUND_COLOR
from database.seeders import seed_default_admin
from router import resolve_view, route_guard
from services.session_service import get_current_user_id, set_session_value
from utils.route_utils import normalize_route


def main(page: ft.Page) -> None:
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BACKGROUND_COLOR
    page.padding = 0
    page.spacing = 0
    page.window_min_width = 1100
    page.window_min_height = 700
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    }
    page.theme = ft.Theme(font_family="Inter")
    if not isinstance(getattr(page, "data", None), dict):
        page.data = {}
    seed_default_admin()

    if get_current_user_id(page) is None:
        set_session_value(page, "user_id", None)
        set_session_value(page, "user_role", "")
        set_session_value(page, "user_name", "")
        set_session_value(page, "user_email", "")

    def apply_route(forced_route: str | None = None) -> None:
        current = normalize_route(forced_route or page.route or "/")
        safe_route = route_guard(page, current)

        if safe_route != current:
            page.go(safe_route)
            apply_route(safe_route)
            return

        try:
            view = resolve_view(page, safe_route)
            if view is None:
                raise RuntimeError(f"Page builder returned no view for route: {safe_route}")
        except Exception as exc:
            print(f"[BODYQUEST] Route error ({safe_route}): {exc}")
            traceback.print_exc()
            from pages.auth.error import error_view

            view = error_view(page, str(exc))

        page.views.clear()
        page.views.append(view)
        page.update()

    def on_route_change(event: ft.RouteChangeEvent | None = None) -> None:
        route = getattr(event, "route", None) if event is not None else None
        apply_route(route)

    def on_view_pop(event: ft.ViewPopEvent) -> None:
        if event.view is not None and event.view in page.views:
            page.views.remove(event.view)
        if page.views:
            page.go(page.views[-1].route)
        else:
            page.go("/")

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop
    apply_route("/")


if __name__ == "__main__":
    ft.run(main)
