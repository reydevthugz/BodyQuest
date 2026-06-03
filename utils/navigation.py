"""Shared Flet navigation helpers."""
from __future__ import annotations

import flet as ft

from utils.route_utils import normalize_route


def go(page: ft.Page, route: str) -> None:
    """Navigate to route and refresh the page (required after modals and forms)."""
    target = normalize_route(route)
    page.go(target)
    page.update()
