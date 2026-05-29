import flet as ft

from components.cards import glass_card, list_row
from components.theme import MUTED_TEXT_COLOR, TEXT_COLOR
from services.admin_service import get_leaderboard
from utils.messages import NO_LEADERBOARD


def build_content() -> ft.Control:
    rows = get_leaderboard()
    if not rows:
        return glass_card(
            ft.Column(
                spacing=10,
                controls=[
                    ft.Text("Leaderboard", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Text(NO_LEADERBOARD, color=MUTED_TEXT_COLOR),
                ],
            )
        )
    controls = []
    for idx, r in enumerate(rows, start=1):
        controls.append(
            list_row(
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(f"#{idx} {r['full_name']}", color=TEXT_COLOR, weight=ft.FontWeight.W_600),
                        ft.Text(r["email"], color=MUTED_TEXT_COLOR, size=12),
                        ft.Text(
                            f"Achievements: {r['total_achievements']} | Completed goals: {r['completed_goals']} | Completed workout days: {r['completed_workout_days']}",
                            color=MUTED_TEXT_COLOR,
                            size=11,
                        ),
                        ft.Text(f"Current goal: {r.get('current_goal') or 'No active goal'} | Progress: {r.get('current_progress') or 0}%", color=MUTED_TEXT_COLOR, size=11),
                    ],
                ),
            )
        )
    return ft.Column(spacing=12, controls=[ft.Text("Leaderboard", size=28, color=TEXT_COLOR, weight=ft.FontWeight.BOLD), glass_card(ft.Column(spacing=8, controls=controls))])


def leaderboard_view(page: ft.Page) -> ft.View:
    from components.admin_layout import admin_shell

    return admin_shell(page, "leaderboard", build_content())
