import flet as ft

from components.cards import glass_card, list_row
from components.theme import MUTED_TEXT_COLOR, TEXT_COLOR, themed_dropdown, themed_text_field
from services.admin_service import get_all_achievements
from services.session_service import get_session_value, set_session_value
from utils.date_utils import format_datetime
from utils.messages import NO_ACHIEVEMENTS_ADMIN


def build_content(page: ft.Page) -> ft.Control:
    search_val = str(get_session_value(page, "admin_ach_search", "") or "")
    badge_val = str(get_session_value(page, "admin_ach_badge", "All") or "All")
    badge_dropdown = themed_dropdown(
        value=badge_val,
        width=220,
        options=[ft.dropdown.Option(x) for x in ["All", "starter", "streak", "consistency", "cardio", "strength", "flexibility", "champion", "switch"]],
    )
    badge_dropdown.on_change = lambda e: (set_session_value(page, "admin_ach_badge", e.control.value), page.go("/admin/achievements"))
    rows = get_all_achievements(search=search_val or None, badge_type=badge_val)
    if not rows:
        body = ft.Text(NO_ACHIEVEMENTS_ADMIN, color=MUTED_TEXT_COLOR)
    else:
        body = ft.Column(
            spacing=8,
            controls=[
                list_row(
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(f"{r['name']} • {r['full_name']}", color=TEXT_COLOR, weight=ft.FontWeight.W_600),
                            ft.Text(r["email"], color=MUTED_TEXT_COLOR, size=12),
                            ft.Text(f"Goal: {r.get('goal_type') or 'N/A'} | Badge: {r.get('badge_type') or '-'}", color=MUTED_TEXT_COLOR, size=11),
                            ft.Text(f"Earned: {format_datetime(r.get('earned_at'))}", color=MUTED_TEXT_COLOR, size=11),
                        ],
                    ),
                )
                for r in rows
            ],
        )
    return ft.Column(
        spacing=12,
        controls=[
            ft.Text("All Achievements", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=themed_text_field(
                                value=search_val,
                                hint_text="Search by user or achievement",
                                on_submit=lambda e: (set_session_value(page, "admin_ach_search", e.control.value or ""), page.go("/admin/achievements")),
                            ),
                        ),
                        badge_dropdown,
                    ],
                )
            ),
            glass_card(body),
        ],
    )


def all_achievements_view(page: ft.Page) -> ft.View:
    from components.admin_layout import admin_shell

    return admin_shell(page, "achievements", build_content(page))
