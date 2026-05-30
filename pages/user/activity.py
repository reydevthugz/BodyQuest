import asyncio

import flet as ft

from components.cards import glass_card, status_badge
from components.theme import ERROR_TEXT_COLOR, MUTED_TEXT_COLOR, PRIMARY_COLOR, TEXT_COLOR, feedback_text
from components.ui import neon_button, soft_button
from controllers.progress_controller import handle_complete_activity, handle_start_timer
from pages.user.common import user_shell
from services.plan_service import get_active_goal, get_latest_completed_goal
from services.progress_service import get_activity_day, resolve_day_status
from services.session_service import get_current_user_id
from utils.messages import NO_ACTIVE_PLAN


def _format_time(total_seconds: int) -> str:
    minutes, seconds = divmod(max(total_seconds, 0), 60)
    return f"{minutes:02d}:{seconds:02d}"


def activity_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        page.go("/login")
        return user_shell(page, "activity", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)), "Activity")

    goal = get_active_goal(user_id)
    if not goal:
        completed = get_latest_completed_goal(user_id)
        if completed:
            content = glass_card(
                ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("Goal Completed!", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"You finished your {completed['goal_type']} plan. Start a new goal anytime.",
                            color=MUTED_TEXT_COLOR,
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                neon_button("View Achievements", ft.Icons.MILITARY_TECH, lambda _: page.go("/user/achievements")),
                                soft_button("View History", ft.Icons.HISTORY, lambda _: page.go("/user/history")),
                                neon_button("Start New Plan", ft.Icons.TUNE, lambda _: page.go("/user/goal-setup")),
                            ],
                        ),
                    ],
                )
            )
            return user_shell(page, "activity", content, completed["goal_type"])
        content = glass_card(
            ft.Column(
                spacing=12,
                controls=[
                    ft.Text("No Active Plan", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Text(NO_ACTIVE_PLAN, color=MUTED_TEXT_COLOR),
                    neon_button("Choose Fitness Goal", ft.Icons.TUNE, lambda _: page.go("/user/goal-setup")),
                ],
            )
        )
        return user_shell(page, "activity", content, "No Active Plan")

    day, read_only = get_activity_day(user_id, goal["id"], page)
    if not day:
        content = glass_card(
            ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Goal completed! Great work.", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        spacing=10,
                        controls=[
                            neon_button("View Achievements", ft.Icons.MILITARY_TECH, lambda _: page.go("/user/achievements")),
                            soft_button("View History", ft.Icons.HISTORY, lambda _: page.go("/user/history")),
                        ],
                    ),
                ],
            )
        )
        return user_shell(page, "activity", content, goal["goal_type"])

    goal_id = goal["id"]
    day_id = int(day["id"])
    display_status = resolve_day_status(day)
    estimated_seconds = int(day.get("estimated_minutes") or 20) * 60
    timer_state = {"elapsed": 0, "running": False, "started_server": bool(day.get("started_at"))}
    timer_task = {"handle": None}

    notice = feedback_text()
    timer_text = ft.Text("00:00", size=36, color=PRIMARY_COLOR, weight=ft.FontWeight.BOLD)
    countdown_text = ft.Text("", color=MUTED_TEXT_COLOR, size=12)
    complete_btn = neon_button("Mark as Completed", ft.Icons.CHECK_CIRCLE, lambda _: None)
    complete_btn.disabled = not read_only and not timer_state["started_server"]

    async def tick_timer():
        while timer_state["running"]:
            await asyncio.sleep(1)
            if not timer_state["running"]:
                break
            timer_state["elapsed"] += 1
            timer_text.value = _format_time(timer_state["elapsed"])
            remaining = max(estimated_seconds - timer_state["elapsed"], 0)
            countdown_text.value = f"Countdown: {_format_time(remaining)} remaining"
            page.update()

    def stop_timer_task():
        timer_state["running"] = False
        if timer_task["handle"] and not timer_task["handle"].done():
            timer_task["handle"].cancel()
        timer_task["handle"] = None

    def refresh_complete_button():
        complete_btn.disabled = read_only or not timer_state["started_server"]

    def start_timer(_: ft.ControlEvent):
        if read_only:
            return
        result = handle_start_timer(page, goal_id, day_id)
        if not result["success"]:
            notice.value = result["message"] or ""
            notice.color = ERROR_TEXT_COLOR
            page.update()
            return
        timer_state["started_server"] = True
        timer_state["running"] = True
        refresh_complete_button()
        stop_timer_task()
        timer_task["handle"] = page.run_task(tick_timer)
        page.update()

    def pause_timer(_: ft.ControlEvent):
        timer_state["running"] = False
        stop_timer_task()
        page.update()

    def reset_timer(_: ft.ControlEvent):
        timer_state["running"] = False
        timer_state["elapsed"] = 0
        timer_text.value = "00:00"
        countdown_text.value = f"Target: {day.get('estimated_minutes', 20)} min"
        stop_timer_task()
        page.update()

    def complete(_: ft.ControlEvent):
        if read_only:
            return
        stop_timer_task()
        result = handle_complete_activity(page, goal_id, day_id, timer_state["elapsed"])
        notice.value = result["message"] or ""
        if result["success"]:
            page.snack_bar = ft.SnackBar(ft.Text(result["message"]))
            page.snack_bar.open = True
            page.go(result["data"]["route"])
        else:
            notice.color = ERROR_TEXT_COLOR
            page.update()

    complete_btn.on_click = complete

    timer_card = glass_card(
        ft.Column(
            spacing=12,
            controls=[
                ft.Text("Task Timer", color=TEXT_COLOR, size=16, weight=ft.FontWeight.W_600),
                timer_text,
                countdown_text,
                ft.Row(
                    spacing=10,
                    controls=[
                        neon_button("Start Timer", ft.Icons.PLAY_ARROW, start_timer),
                        soft_button("Pause", ft.Icons.PAUSE, pause_timer),
                        soft_button("Reset", ft.Icons.REPLAY, reset_timer),
                    ],
                ),
            ],
        ),
        padding=20,
    )

    header_badges = [status_badge(_status_label(display_status), _status_tone(display_status))]
    if read_only:
        header_badges.append(status_badge("View Only", "blue"))

    content = ft.Column(
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Day {day['day_number']} Activity", size=30, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Row(spacing=8, controls=header_badges),
                ],
            ),
            glass_card(
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(day["title"], color=TEXT_COLOR, size=20, weight=ft.FontWeight.W_600),
                        ft.Text(f"Warm-up: {day['warmup']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Main Activity: {day['main_activity']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Cooldown: {day['cooldown']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Safety Tip: {day['safety_tip']}", color=PRIMARY_COLOR),
                        ft.Text(f"Estimated Minutes: {day['estimated_minutes']}", color=MUTED_TEXT_COLOR),
                    ],
                )
            ),
            timer_card if not read_only else ft.Container(),
            complete_btn if not read_only else soft_button("Back to Timeline", ft.Icons.TIMELINE, lambda _: page.go("/user/timeline")),
            notice,
        ],
    )
    countdown_text.value = f"Target: {day.get('estimated_minutes', 20)} min"
    return user_shell(page, "activity", content, goal["goal_type"])


def _status_tone(display_status: str) -> str:
    mapping = {
        "completed": "accent",
        "current": "cyan",
        "in_progress": "aqua",
        "locked": "blue",
    }
    return mapping.get(display_status, "cyan")


def _status_label(display_status: str) -> str:
    mapping = {
        "completed": "Completed",
        "current": "Current",
        "in_progress": "In Progress",
        "locked": "Locked",
    }
    return mapping.get(display_status, display_status.title())
