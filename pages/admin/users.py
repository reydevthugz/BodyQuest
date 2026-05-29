import flet as ft

from components.cards import glass_card
from components.buttons import link_button
from components.cards import list_row
from components.theme import MUTED_TEXT_COLOR, PRIMARY_COLOR, TEXT_COLOR, themed_dropdown, themed_text_field
from controllers.admin_controller import get_users_data
from services.session_service import get_session_value, set_session_value
from utils.messages import NO_REGISTERED_USERS


def build_content(page: ft.Page) -> ft.Control:
    search_value = str(get_session_value(page, "admin_users_search", "") or "")
    status_value = str(get_session_value(page, "admin_users_filter", "All Users") or "All Users")
    data = get_users_data(page, search=search_value or None, status_filter=status_value)

    search_field = themed_text_field(
        value=search_value,
        hint_text="Search by name or email",
        on_submit=lambda e: (set_session_value(page, "admin_users_search", e.control.value or ""), page.go("/admin/users")),
    )
    filter_dd = themed_dropdown(
        value=status_value,
        width=220,
        options=[ft.dropdown.Option(x) for x in ["All Users", "Active", "Inactive", "Completed Goal", "Changed Plan"]],
    )
    filter_dd.on_change = lambda e: (set_session_value(page, "admin_users_filter", e.control.value), page.go("/admin/users"))

    if not data:
        empty_msg = NO_REGISTERED_USERS if not search_value and status_value == "All Users" else "No users match your search or filter."
        table = ft.Text(empty_msg, color=MUTED_TEXT_COLOR)
    else:
        rows = []
        for user in data:
            status_label = str(user.get("status_tag") or "inactive").replace("_", " ").title()
            last = user.get("last_activity_at")
            last_text = last.strftime("%Y-%m-%d") if last else "No activity"
            rows.append(
                list_row(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(user["full_name"], color=TEXT_COLOR, weight=ft.FontWeight.W_600),
                                    ft.Text(user["email"], color=MUTED_TEXT_COLOR, size=12),
                                    ft.Text(
                                        f"Goal: {user.get('current_goal') or 'No active goal'} | Progress: {user.get('progress_percent') or 0}% | Achievements: {user.get('total_achievements') or 0}",
                                        color=MUTED_TEXT_COLOR,
                                        size=11,
                                    ),
                                    ft.Text(f"Status: {status_label} | Last activity: {last_text}", color=MUTED_TEXT_COLOR, size=11),
                                ],
                            ),
                            link_button(
                                "View Details",
                                lambda _, uid=user["id"]: (set_session_value(page, "selected_user_id", uid), page.go("/admin/users/details")),
                            ),
                        ],
                    ),
                )
            )
        table = ft.Column(spacing=8, controls=rows)

    return ft.Column(
        spacing=12,
        controls=[
            ft.Text("User Management", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            glass_card(ft.Row(spacing=10, controls=[ft.Container(expand=True, content=search_field), filter_dd])),
            glass_card(table),
        ],
    )


def users_view(page: ft.Page) -> ft.View:
    from components.admin_layout import admin_shell

    return admin_shell(page, "users", build_content(page))
