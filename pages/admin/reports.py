import flet as ft

from components.cards import glass_card, stat_tile
from components.theme import MUTED_TEXT_COLOR, STAT_COLORS, TEXT_COLOR
from services.admin_service import get_reports_summary
from utils.date_utils import format_datetime
from utils.messages import NO_REPORT_DATA


def build_content() -> ft.Control:
    report = get_reports_summary()
    if report.get("total_users", 0) == 0:
        return ft.Column(
            spacing=12,
            controls=[
                ft.Text("Reports", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                glass_card(ft.Text(NO_REPORT_DATA, color=MUTED_TEXT_COLOR)),
            ],
        )
    return ft.Column(
        spacing=12,
        controls=[
            ft.Text("Reports", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(col={"sm": 6, "md": 4}, content=stat_tile("Total Users", str(report["total_users"]), ft.Icons.GROUPS_2_ROUNDED, STAT_COLORS[0])),
                    ft.Container(col={"sm": 6, "md": 4}, content=stat_tile("Active Users", str(report["active_users"]), ft.Icons.MONITOR_HEART, STAT_COLORS[1])),
                    ft.Container(col={"sm": 6, "md": 4}, content=stat_tile("Completed Goals", str(report["completed_goals_count"]), ft.Icons.EMOJI_EVENTS, STAT_COLORS[2])),
                ]
            ),
            glass_card(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(f"Most selected goal: {report['most_selected_goal']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Average completion progress: {report['average_completion_progress']}%", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Changed/replaced plans: {report['changed_plans_count']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Most earned achievement: {report['most_earned_achievement']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Total workout days completed: {report['total_workout_days_completed']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Total active plans: {report['total_active_plans']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Total completed plans: {report['total_completed_plans']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Total replaced plans: {report['total_replaced_plans']}", color=MUTED_TEXT_COLOR),
                    ],
                )
            ),
            glass_card(
                ft.Column(
                    spacing=6,
                    controls=[ft.Text("Recently Active Users", color=TEXT_COLOR, size=18, weight=ft.FontWeight.W_600)]
                    + (
                        [ft.Text("No data yet", color=MUTED_TEXT_COLOR)]
                        if not report["recently_active_users"]
                        else [
                            ft.Text(
                                f"{r['full_name']} • {r['action']} • {format_datetime(r.get('created_at'))}",
                                color=MUTED_TEXT_COLOR,
                                size=12,
                            )
                            for r in report["recently_active_users"]
                        ]
                    ),
                )
            ),
        ],
    )


def reports_view(page: ft.Page) -> ft.View:
    from components.admin_layout import admin_shell

    return admin_shell(page, "reports", build_content())
