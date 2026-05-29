import flet as ft

from components.cards import glass_card, stat_tile, status_badge
from components.theme import BORDER_SUBTLE, MUTED_TEXT_COLOR, PRIMARY_COLOR, PROGRESS_TRACK, SECONDARY_COLOR, STAT_COLORS, SURFACE_SOFT, TEXT_COLOR, glass_border
from controllers.admin_controller import get_dashboard_data
from pages.admin._helpers import achievement_row, leader_row, progress_row
from services.session_service import get_current_user_name
from utils.date_utils import format_datetime
from utils.messages import NO_ACTIVE_PLANS, NO_REGISTERED_USERS


def build_content(admin_name: str | None = None) -> ft.Control:
    name = admin_name or "Admin"
    stats = get_dashboard_data()
    no_users = stats.get("total_users", 0) == 0
    distribution_controls = (
        [ft.Text(NO_ACTIVE_PLANS, color=MUTED_TEXT_COLOR)]
        if not stats["goal_distribution"]
        else [progress_row(item["goal_type"], max(min(item["ratio"] / 100, 1), 0)) for item in stats["goal_distribution"][:5]]
    )
    recent_activity_controls = (
        [ft.Text(NO_REGISTERED_USERS if no_users else "No user activity yet.", color=MUTED_TEXT_COLOR)]
        if not stats["recent_user_activity"]
        else [
            achievement_row(
                f"{item['full_name']} • {item['action'].replace('_', ' ').title()}",
                format_datetime(item.get("created_at")),
            )
            for item in stats["recent_user_activity"][:5]
        ]
    )
    top_controls = (
        [ft.Text(NO_REGISTERED_USERS if no_users else NO_ACTIVE_PLANS, color=MUTED_TEXT_COLOR)]
        if not stats["top_performing_users"]
        else [
            leader_row(
                str(idx + 1),
                user["full_name"],
                user.get("current_goal") or "No active goal",
                max(min((user.get("current_progress") or 0) / 100, 1), 0),
                str(user.get("total_achievements") or 0),
            )
            for idx, user in enumerate(stats["top_performing_users"][:10])
        ]
    )
    return ft.Column(
        spacing=18,
        controls=[
            glass_card(
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            col={"md": 8},
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Row(spacing=10, controls=[status_badge("Admin Mode", "aqua"), status_badge("Monitoring Active", "cyan")]),
                                    ft.Text(f"Welcome, {name}", size=36, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                                    ft.Text("System overview at a glance with live goal progress and achievement signals.", size=14, color=MUTED_TEXT_COLOR),
                                ],
                            ),
                        ),
                        ft.Container(
                            col={"md": 4},
                            content=ft.Container(
                                height=110,
                                border_radius=16,
                                bgcolor=SURFACE_SOFT,
                                border=glass_border(1, BORDER_SUBTLE),
                                padding=14,
                                content=ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text("Weekly Adoption", color=MUTED_TEXT_COLOR, size=12),
                                        ft.Text(str(stats["active_users"]), color=PRIMARY_COLOR, size=26, weight=ft.FontWeight.BOLD),
                                        ft.ProgressBar(
                                            value=(stats["active_users"] / stats["total_users"]) if stats["total_users"] else 0,
                                            color=SECONDARY_COLOR,
                                            bgcolor=PROGRESS_TRACK,
                                            height=8,
                                        ),
                                    ],
                                ),
                            ),
                        ),
                    ]
                ),
                padding=24,
            ),
            ft.ResponsiveRow(
                run_spacing=12,
                controls=[
                    ft.Container(col={"sm": 6, "md": 4, "lg": 2}, content=stat_tile("Total Users", str(stats["total_users"]), ft.Icons.GROUPS_2_ROUNDED, STAT_COLORS[0])),
                    ft.Container(col={"sm": 6, "md": 4, "lg": 2}, content=stat_tile("Active Users", str(stats["active_users"]), ft.Icons.MONITOR_HEART, STAT_COLORS[1])),
                    ft.Container(col={"sm": 6, "md": 4, "lg": 2}, content=stat_tile("Completed Goals", str(stats["completed_goals"]), ft.Icons.EMOJI_EVENTS, STAT_COLORS[2])),
                    ft.Container(col={"sm": 6, "md": 4, "lg": 2}, content=stat_tile("Achievements", str(stats["total_achievements"]), ft.Icons.MILITARY_TECH, STAT_COLORS[3])),
                    ft.Container(col={"sm": 6, "md": 4, "lg": 2}, content=stat_tile("In Progress", str(stats["plans_in_progress"]), ft.Icons.TRENDING_UP, STAT_COLORS[4])),
                    ft.Container(col={"sm": 6, "md": 4, "lg": 2}, content=stat_tile("Changed Plans", str(stats["changed_plans"]), ft.Icons.SYNC_ALT, STAT_COLORS[5])),
                ],
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(col={"md": 6}, content=glass_card(ft.Column(spacing=14, controls=[ft.Text("Goal Distribution", size=20, color=TEXT_COLOR, weight=ft.FontWeight.W_600)] + distribution_controls))),
                    ft.Container(col={"md": 6}, content=glass_card(ft.Column(spacing=12, controls=[ft.Text("Recent User Activity", size=20, color=TEXT_COLOR, weight=ft.FontWeight.W_600)] + recent_activity_controls))),
                ]
            ),
            glass_card(ft.Column(spacing=12, controls=[ft.Text("Top Performing Users", size=20, color=TEXT_COLOR, weight=ft.FontWeight.W_600)] + top_controls)),
        ],
    )


def dashboard_view(page: ft.Page) -> ft.View:
    from components.admin_layout import admin_shell

    return admin_shell(page, "dashboard", build_content(get_current_user_name(page)))
