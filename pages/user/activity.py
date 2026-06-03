import asyncio
from datetime import datetime

import flet as ft

from components.cards import glass_card, status_badge
from components.theme import ERROR_TEXT_COLOR, MUTED_TEXT_COLOR, PRIMARY_COLOR, TEXT_COLOR, feedback_text
from components.ui import neon_button, soft_button
from controllers.progress_controller import handle_complete_activity, handle_start_timer, handle_stop_task
from components.dialogs import show_change_plan_dialog
from pages.user.common import user_shell
from services.plan_service import get_active_goal, get_latest_completed_goal
from services.progress_service import get_activity_day, resolve_day_status
from services.session_service import get_current_user_id, get_session_value
from utils.messages import CHOOSE_GOAL_JOURNEY, PLAN_COMPLETED, TASK_STARTED, TASK_STOPPED
from utils.navigation import go


def _format_time(total_seconds: int) -> str:
    minutes, seconds = divmod(max(total_seconds, 0), 60)
    return f"{minutes:02d}:{seconds:02d}"


def _elapsed_from_started_at(started_at) -> int:
    if not started_at:
        return 0
    if isinstance(started_at, datetime):
        started = started_at
    else:
        try:
            started = datetime.fromisoformat(str(started_at))
        except (TypeError, ValueError):
            return 0
    return max(int((datetime.now() - started).total_seconds()), 0)


def _no_active_plan_view(page: ft.Page, user_id: int) -> ft.View:
    pending_goal = str(get_session_value(page, "selected_goal", "") or "").strip()
    if pending_goal:
        go(page, "/user/plan-preview")
        return user_shell(
            page,
            "activity",
            glass_card(ft.Text("Redirecting to plan preview...", color=MUTED_TEXT_COLOR)),
            "Activity",
        )

    completed = get_latest_completed_goal(user_id)
    if completed:
        content = glass_card(
            ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Goal Completed!", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Text(PLAN_COMPLETED, color=MUTED_TEXT_COLOR),
                    ft.Row(
                        spacing=10,
                        controls=[
                            neon_button("View Achievements", ft.Icons.MILITARY_TECH, lambda _: go(page, "/user/achievements")),
                            soft_button("View History", ft.Icons.HISTORY, lambda _: go(page, "/user/history")),
                            neon_button("Change Plan", ft.Icons.SYNC, lambda _: show_change_plan_dialog(page)),
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
                ft.Text(CHOOSE_GOAL_JOURNEY, color=MUTED_TEXT_COLOR),
                neon_button("Choose Fitness Goal", ft.Icons.TUNE, lambda _: go(page, "/user/goal-setup")),
            ],
        )
    )
    return user_shell(page, "activity", content, "No Active Plan")


def activity_view(page: ft.Page) -> ft.View:
    user_id = get_current_user_id(page)
    if not user_id:
        go(page, "/login")
        return user_shell(page, "activity", glass_card(ft.Text("Please log in to continue.", color=MUTED_TEXT_COLOR)), "Activity")

    goal = get_active_goal(user_id)
    if not goal:
        return _no_active_plan_view(page, user_id)

    day, read_only = get_activity_day(user_id, goal["id"], page)
    if not day:
        content = glass_card(
            ft.Column(
                spacing=12,
                controls=[
                    ft.Text("Congratulations!", size=24, color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    ft.Text(PLAN_COMPLETED, color=MUTED_TEXT_COLOR),
                    ft.Row(
                        spacing=10,
                        controls=[
                            neon_button("View Achievements", ft.Icons.MILITARY_TECH, lambda _: go(page, "/user/achievements")),
                            soft_button("View History", ft.Icons.HISTORY, lambda _: go(page, "/user/history")),
                            neon_button("Back to Dashboard", ft.Icons.DASHBOARD, lambda _: go(page, "/user/dashboard")),
                        ],
                    ),
                ],
            )
        )
        return user_shell(page, "activity", content, goal["goal_type"])

    goal_id = goal["id"]
    day_id = int(day["id"])
    display_status = resolve_day_status(day)
    server_elapsed = _elapsed_from_started_at(day.get("started_at"))
    initial_elapsed = server_elapsed if day.get("started_at") else 0
    timer_state = {
        "elapsed": initial_elapsed,
        "running": False,
        "started_server": bool(day.get("started_at")),
        "is_stopped": display_status == "stopped",
    }
    timer_task = {"handle": None}

    notice = feedback_text()
    if timer_state["is_stopped"] and not read_only:
        notice.value = TASK_STOPPED
    elif timer_state["started_server"] and display_status == "in_progress" and not read_only:
        notice.value = TASK_STARTED

    timer_text = ft.Text(_format_time(initial_elapsed), size=36, color=PRIMARY_COLOR, weight=ft.FontWeight.BOLD)
    countdown_text = ft.Text("", color=MUTED_TEXT_COLOR, size=12)
    complete_btn = neon_button("Mark as Completed", ft.Icons.CHECK_CIRCLE, lambda _: None)
    complete_btn.disabled = not read_only and not timer_state["started_server"]
    start_btn = neon_button("Start / Resume", ft.Icons.PLAY_ARROW, lambda _: None)
    stop_btn = soft_button("Stop", ft.Icons.STOP_CIRCLE, lambda _: None)

    async def tick_timer():
        while timer_state["running"]:
            await asyncio.sleep(1)
            if not timer_state["running"]:
                break
            timer_state["elapsed"] += 1
            timer_text.value = _format_time(timer_state["elapsed"])
            countdown_text.value = (
                f"Elapsed: {_format_time(timer_state['elapsed'])} • Target: {day.get('estimated_minutes', 20)} min"
            )
            page.update()

    def stop_timer_task():
        timer_state["running"] = False
        if timer_task["handle"] and not timer_task["handle"].done():
            timer_task["handle"].cancel()
        timer_task["handle"] = None

    def refresh_timer_buttons():
        if read_only:
            start_btn.disabled = True
            stop_btn.disabled = True
            return
        start_btn.disabled = timer_state["running"] or (
            timer_state["started_server"] and not timer_state["is_stopped"]
        )
        stop_btn.disabled = (
            not timer_state["started_server"] or timer_state["is_stopped"] or not timer_state["running"]
        )

    def refresh_complete_button():
        complete_btn.disabled = read_only or not timer_state["started_server"]

    def start_local_timer():
        if timer_state["running"]:
            return
        timer_state["running"] = True
        stop_timer_task()
        timer_task["handle"] = page.run_task(tick_timer)

    def start_task(_: ft.ControlEvent):
        if read_only:
            return
        result = handle_start_timer(page, goal_id, day_id)
        if not result["success"]:
            notice.value = result["message"] or ""
            notice.color = ERROR_TEXT_COLOR
            page.update()
            return
        timer_state["started_server"] = True
        timer_state["is_stopped"] = False
        if timer_state["elapsed"] == 0:
            timer_state["elapsed"] = _elapsed_from_started_at(day.get("started_at"))
        notice.value = result.get("data", {}).get("message") or TASK_STARTED
        notice.color = MUTED_TEXT_COLOR
        refresh_complete_button()
        start_local_timer()
        refresh_timer_buttons()
        page.update()

    def stop_task(_: ft.ControlEvent):
        if read_only:
            return
        stop_timer_task()
        result = handle_stop_task(page, goal_id, day_id)
        notice.value = result["message"] or ""
        if result["success"]:
            timer_state["is_stopped"] = True
            timer_state["running"] = False
            notice.color = MUTED_TEXT_COLOR
        else:
            notice.color = ERROR_TEXT_COLOR
        refresh_timer_buttons()
        page.update()

    def complete(_: ft.ControlEvent):
        if read_only:
            return
        stop_timer_task()
        duration = max(timer_state["elapsed"], server_elapsed, _elapsed_from_started_at(day.get("started_at")))
        result = handle_complete_activity(page, goal_id, day_id, duration)
        notice.value = result["message"] or ""
        if result["success"]:
            page.snack_bar = ft.SnackBar(ft.Text(result["message"]))
            page.snack_bar.open = True
            go(page, result["data"]["route"])
        else:
            notice.color = ERROR_TEXT_COLOR
            page.update()

    complete_btn.on_click = complete
    start_btn.on_click = start_task
    stop_btn.on_click = stop_task

    timer_card = glass_card(
        ft.Column(
            spacing=12,
            controls=[
                ft.Text("Task Timer", color=TEXT_COLOR, size=16, weight=ft.FontWeight.W_600),
                timer_text,
                countdown_text,
                ft.Row(spacing=10, controls=[start_btn, stop_btn]),
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
                        ft.Text(
                            f"Description: {day.get('description') or day['main_activity']}",
                            color=MUTED_TEXT_COLOR,
                        ),
                        ft.Text(f"Main Activity: {day['main_activity']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Warm-up: {day['warmup']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Cooldown: {day['cooldown']}", color=MUTED_TEXT_COLOR),
                        ft.Text(f"Safety Tip: {day['safety_tip']}", color=PRIMARY_COLOR),
                        ft.Text(f"Estimated Minutes: {day['estimated_minutes']}", color=MUTED_TEXT_COLOR),
                    ],
                )
            ),
            timer_card if not read_only else ft.Container(),
            complete_btn if not read_only else soft_button("Back to Timeline", ft.Icons.TIMELINE, lambda _: go(page, "/user/timeline")),
            notice,
        ],
    )
    countdown_text.value = f"Target: {day.get('estimated_minutes', 20)} min"
    if initial_elapsed > 0:
        countdown_text.value = (
            f"Elapsed: {_format_time(initial_elapsed)} • Target: {day.get('estimated_minutes', 20)} min"
        )

    refresh_timer_buttons()
    if not read_only and display_status == "in_progress" and timer_state["started_server"] and not timer_state["is_stopped"]:
        start_local_timer()
        refresh_timer_buttons()

    return user_shell(page, "activity", content, goal["goal_type"])


def _status_tone(display_status: str) -> str:
    mapping = {
        "completed": "accent",
        "current": "cyan",
        "in_progress": "aqua",
        "stopped": "blue",
        "locked": "blue",
    }
    return mapping.get(display_status, "cyan")


def _status_label(display_status: str) -> str:
    mapping = {
        "completed": "Completed",
        "current": "Current",
        "in_progress": "In Progress",
        "stopped": "Stopped",
        "locked": "Locked",
    }
    return mapping.get(display_status, display_status.title())
