"""
Phase 9 — automated stability tests (no Flet GUI).
Run: py scripts/validate_phase9.py
"""
from __future__ import annotations

import importlib
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, LEGACY_ADMIN_EMAIL

PASS: list[str] = []
FAIL: list[str] = []


def ok(msg: str) -> None:
    PASS.append(msg)
    print(f"  [OK] {msg}")


def bad(msg: str) -> None:
    FAIL.append(msg)
    print(f"  [FAIL] {msg}")


def _complete_day_with_timer(uid: int, gid: int, workout_day_id: int):
    from services.progress_service import complete_current_day, start_task_timer

    start_task_timer(uid, gid, workout_day_id)
    return complete_current_day(uid, gid, workout_day_id)


class MockPage:
    def __init__(self, route: str = "/login", data: dict | None = None):
        self.route = route
        self.data = data if data is not None else {}
        self.session_id = f"phase9-{id(self)}"
        self.width = 1280
        self.height = 800

    def go(self, route: str) -> None:
        self.route = route

    def update(self) -> None:
        pass


def _login_page(page: MockPage, email: str, password: str) -> dict:
    from controllers.auth_controller import handle_login

    return handle_login(page, email, password)


def _cleanup_test_user(email: str) -> None:
    from database.connection import get_connection

    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE email = %s AND role = 'user'", (email,))
        row = cur.fetchone()
        if not row:
            return
        uid = int(row["id"])
        cur.execute("SELECT id FROM user_goals WHERE user_id = %s", (uid,))
        goal_ids = [int(g["id"]) for g in cur.fetchall()]
        for gid in goal_ids:
            cur.execute("DELETE FROM workout_days WHERE goal_id = %s", (gid,))
        cur.execute("DELETE FROM achievements WHERE user_id = %s", (uid,))
        cur.execute("DELETE FROM progress_logs WHERE user_id = %s", (uid,))
        cur.execute("DELETE FROM user_goals WHERE user_id = %s", (uid,))
        cur.execute("DELETE FROM users WHERE id = %s", (uid,))
        conn.commit()


def test_imports() -> None:
    modules = [
        "main",
        "app",
        "router",
        "config.settings",
        "database.connection",
        "database.migrations",
        "database.seeders",
        "services.auth_service",
        "services.plan_service",
        "services.progress_service",
        "services.admin_service",
        "services.achievement_service",
        "controllers.auth_controller",
        "controllers.goal_controller",
        "controllers.progress_controller",
        "controllers.admin_controller",
        "pages.auth.login",
        "pages.auth.signup",
        "pages.user.dashboard",
        "pages.user.goal_setup",
        "pages.user.plan_preview",
        "pages.user.activity",
        "pages.admin.dashboard",
        "pages.admin.users",
        "pages.admin.__init__",
    ]
    for mod in modules:
        try:
            importlib.import_module(mod)
            ok(f"import {mod}")
        except Exception as exc:
            bad(f"import {mod}: {exc}")


def test_database() -> None:
    from database.connection import health_check
    from database.migrations import initialize_database
    from database.seeders import seed_default_admin
    from services.auth_service import login_user

    try:
        health_check()
        ok("MySQL health check")
    except Exception as exc:
        bad(f"MySQL health check: {exc}")
        return

    try:
        initialize_database()
        ok("initialize_database (safe migrations)")
    except Exception as exc:
        bad(f"initialize_database: {exc}")

    created = seed_default_admin()
    ok(f"seed_default_admin (created={created})")

    admin = login_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    if admin and admin.get("role") == "admin":
        ok("admin login")
    else:
        bad("admin login failed")


def test_requirements() -> None:
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8").strip().splitlines()
    allowed = {"flet", "mysql-connector-python"}
    found = {line.strip().lower().split("[")[0] for line in req if line.strip() and not line.strip().startswith("#")}
    extra = found - allowed
    missing = allowed - found
    if not extra and not missing:
        ok("requirements.txt only flet + mysql-connector-python")
    else:
        if extra:
            bad(f"requirements.txt extra packages: {extra}")
        if missing:
            bad(f"requirements.txt missing: {missing}")


def test_route_guard() -> None:
    from router import route_guard
    from services.session_service import clear_current_user, set_current_user

    page = MockPage("/login")

    if route_guard(page, "/user/dashboard") == "/login":
        ok("guest /user/dashboard -> /login")
    else:
        bad("guest /user/dashboard guard")

    if route_guard(page, "/admin/dashboard") == "/login":
        ok("guest /admin/dashboard -> /login")
    else:
        bad("guest /admin/dashboard guard")

    if route_guard(page, "/unknown") == "/404":
        ok("unknown route -> /404")
    else:
        bad("unknown route guard")

    set_current_user(page, {"id": 1, "role": "user", "full_name": "T", "email": "t@test.com"})
    page.route = "/admin/dashboard"
    if route_guard(page, "/admin/dashboard") == "/user/dashboard":
        ok("user /admin/dashboard -> /user/dashboard")
    else:
        bad("user admin guard")

    set_current_user(page, {"id": 99, "role": "admin", "full_name": "A", "email": DEFAULT_ADMIN_EMAIL})
    if route_guard(page, "/user/dashboard") == "/admin/dashboard":
        ok("admin /user/dashboard -> /admin/dashboard")
    else:
        bad("admin user guard")

    clear_current_user(page)


def test_auth_validation() -> None:
    from requests import auth_request

    v = auth_request.validate_signup("", "", "", "")
    if not v["valid"] and len(v["errors"]) >= 3:
        ok("signup empty fields validation")
    else:
        bad("signup empty fields")

    v = auth_request.validate_signup("Name", "bad", "short", "short")
    if not v["valid"]:
        ok("signup invalid email / weak password")
    else:
        bad("signup invalid email/password")

    v = auth_request.validate_signup("Name", "a@b.com", "Password1", "Password2")
    if not v["valid"] and any("match" in e.lower() for e in v["errors"]):
        ok("signup password mismatch")
    else:
        bad("signup mismatch")

    v = auth_request.validate_login("", "")
    if not v["valid"]:
        ok("login empty fields")
    else:
        bad("login empty")


def test_goal_durations() -> None:
    from models.goal_model import GOAL_DURATIONS
    from services.plan_service import generate_plan_days, get_goal_duration, start_new_plan
    from services.plan_service import get_workout_days

    expected = {
        "Lose Weight": 30,
        "Gain Muscle": 30,
        "Improve Endurance": 21,
        "Improve Flexibility": 14,
        "General Fitness": 30,
    }
    for goal, days in expected.items():
        if get_goal_duration(goal) == days and len(generate_plan_days(goal, days)) == days:
            ok(f"goal duration {goal} = {days}")
        else:
            bad(f"goal duration {goal}")

    email = f"phase9.duration.{int(time.time())}@gymbro.test"
    _cleanup_test_user(email)
    from services.auth_service import create_user, login_user

    create_user("Duration Tester", email, "Testpass1")
    user = login_user(email, "Testpass1")
    uid = int(user["id"])
    gid = start_new_plan(uid, "Improve Flexibility")
    days = get_workout_days(gid)
    unlocked = [d for d in days if d["is_unlocked"]]
    if len(days) == 14 and len(unlocked) == 1 and int(unlocked[0]["day_number"]) == 1:
        ok("start plan: 14 days, only day 1 unlocked")
    else:
        bad("start plan unlock state")
    _cleanup_test_user(email)


def test_user_flow() -> None:
    from repositories.goal_repository import GoalRepository
    from services.auth_service import create_user, login_user
    from services.plan_service import get_active_goal, start_new_plan, get_workout_days
    from services.progress_service import complete_current_day, get_user_workout_history
    from services.achievement_service import achievement_exists, get_user_achievements

    email = f"phase9.flow.{int(time.time())}@gymbro.test"
    _cleanup_test_user(email)

    create_user("Flow Tester", email, "Testpass1")
    user = login_user(email, "Testpass1")
    uid = int(user["id"])

    if not get_active_goal(uid):
        ok("new user has no active plan")
    else:
        bad("new user should have no plan")

    gid = start_new_plan(uid, "Improve Flexibility")
    goal = get_active_goal(uid)
    if goal and int(goal["id"]) == gid:
        ok("active plan created")
    else:
        bad("active plan missing")

    days = get_workout_days(gid)
    day1 = days[0]
    ok1, msg1, done1 = _complete_day_with_timer(uid, gid, int(day1["id"]))
    if ok1 and not done1:
        ok("complete day 1 unlocks next")
    else:
        bad(f"complete day 1: {msg1}")

    ok1b, msg1b, _ = complete_current_day(uid, gid, int(day1["id"]))
    if not ok1b:
        ok("cannot complete day 1 twice")
    else:
        bad("duplicate day 1 completion allowed")

    locked = [d for d in get_workout_days(gid) if int(d["day_number"]) == 3][0]
    ok3, msg3, _ = complete_current_day(uid, gid, int(locked["id"]))
    if not ok3:
        ok("cannot skip to locked day 3")
    else:
        bad("skip day allowed")

    # Change plan while still active (after day 2)
    repo = GoalRepository()
    day2 = [d for d in get_workout_days(gid) if int(d["day_number"]) == 2][0]
    ok2, _, _ = _complete_day_with_timer(uid, gid, int(day2["id"]))
    if ok2:
        ok("complete day 2 before change plan")
    else:
        bad("complete day 2 failed")

    old_gid = gid
    gid2 = start_new_plan(uid, "Gain Muscle")
    if int(gid2) != int(old_gid):
        ok("change plan creates new goal")
    else:
        bad("change plan id")

    old = repo.get_goal_by_id(old_gid)
    if old and old["status"] == "replaced" and old.get("replaced_at"):
        ok("old active plan replaced_at saved")
    else:
        bad("old plan not replaced")

    if repo.count_active_goals(uid) == 1:
        ok("single active goal after change")
    else:
        bad(f"active goals count {repo.count_active_goals(uid)}")

    if achievement_exists(uid, None, "Plan Switcher"):
        ok("Plan Switcher awarded once")
    else:
        bad("Plan Switcher missing")

    history = get_user_workout_history(uid)
    if len(history) >= 2:
        ok("history keeps workouts from replaced plan")
    else:
        bad(f"history count {len(history)}")

    # Finish a short plan to verify final-day completion
    flex_gid = start_new_plan(uid, "Improve Flexibility")
    plan_done = False
    while not plan_done:
        current = [d for d in get_workout_days(flex_gid) if d["is_unlocked"] and not d["is_completed"]]
        if not current:
            break
        d = current[0]
        success, message, plan_done = _complete_day_with_timer(uid, flex_gid, int(d["id"]))
        if not success:
            bad(f"complete loop failed: {message}")
            break

    final_goal = repo.get_goal_by_id(flex_gid)
    if final_goal and final_goal["status"] == "completed":
        ok("final day marks goal completed")
    else:
        bad("goal not completed after final day")

    if achievement_exists(uid, flex_gid, "Full Plan Champion"):
        ok("Full Plan Champion awarded")
    else:
        bad("Full Plan Champion missing")

    _cleanup_test_user(email)


def test_timer_and_timeline() -> None:
    from services.auth_service import create_user, login_user
    from services.plan_service import get_workout_days, start_new_plan
    from services.progress_service import complete_current_day, select_timeline_day
    from utils.messages import TASK_LOCKED, TIMER_REQUIRED

    email = f"phase9.timer.{int(time.time())}@gymbro.test"
    _cleanup_test_user(email)
    create_user("Timer Tester", email, "Testpass1")
    user = login_user(email, "Testpass1")
    uid = int(user["id"])
    gid = start_new_plan(uid, "General Fitness")
    days = get_workout_days(gid)
    day1 = days[0]
    locked = [d for d in days if int(d["day_number"]) == 3][0]
    page = MockPage("/user/timeline")

    ok_timer, msg_timer, _ = complete_current_day(uid, gid, int(day1["id"]))
    if not ok_timer and msg_timer == TIMER_REQUIRED:
        ok("timer required before complete")
    else:
        bad(f"timer required check: {msg_timer}")

    ok_sel, msg_sel, _ = select_timeline_day(uid, gid, int(locked["id"]), page)
    if not ok_sel and msg_sel == TASK_LOCKED:
        ok("locked timeline day rejected")
    else:
        bad("locked timeline selection allowed")

    _complete_day_with_timer(uid, gid, int(day1["id"]))
    _cleanup_test_user(email)


def test_admin_stats() -> None:
    from services.admin_service import get_all_users, get_dashboard_stats, get_reports_summary
    from services.auth_service import login_user

    users = get_all_users()
    admin_emails = {DEFAULT_ADMIN_EMAIL, LEGACY_ADMIN_EMAIL}
    if all(u.get("email") not in admin_emails for u in users):
        ok("admin not listed in user management")
    else:
        bad("admin appears in user list")

    stats = get_dashboard_stats()
    for key in (
        "total_users",
        "active_users",
        "completed_goals",
        "total_achievements",
        "plans_in_progress",
        "changed_plans",
    ):
        if key in stats and isinstance(stats[key], int):
            continue
        bad(f"dashboard stat missing {key}")
        break
    else:
        ok("dashboard stats keys present")

    reports = get_reports_summary()
    try:
        _ = int(reports.get("average_completion_progress", 0))
        ok("reports summary no crash")
    except Exception as exc:
        bad(f"reports summary: {exc}")

    admin = login_user(DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    if admin:
        ok("admin credentials still valid")
    else:
        bad("admin credentials")


def test_regression_demo() -> None:
    """Final demo regression: auth, routes, views, logout, 404, admin surfaces."""
    from controllers.auth_controller import handle_login, handle_logout, handle_signup
    from controllers.goal_controller import handle_change_plan, handle_goal_selection, handle_start_plan
    from pages.admin.dashboard import build_content as admin_dashboard_content
    from pages.admin.leaderboard import build_content as leaderboard_content
    from pages.admin.reports import build_content as reports_content
    from router import resolve_view, route_guard
    from services.admin_service import get_all_users, get_leaderboard, get_reports_summary
    from services.plan_service import generate_plan_days, get_latest_completed_goal, get_workout_days
    from services.session_service import clear_current_user, get_current_user_id, is_logged_in, set_session_value
    from utils.date_utils import format_date, format_datetime
    from utils.route_utils import ADMIN_ROUTES, USER_ROUTES

    page = MockPage("/login")

    # 404
    if route_guard(page, "/does-not-exist") == "/404":
        ok("404 route guard")
    else:
        bad("404 route guard")

    view_404 = resolve_view(page, "/404")
    if view_404 is not None:
        ok("404 view resolves")
    else:
        bad("404 view")

    # Signup + login routing
    email = f"phase9.reg.{int(time.time())}@gymbro.test"
    _cleanup_test_user(email)
    signup = handle_signup(page, "Regression User", email, "Testpass1", "Testpass1")
    if signup["success"] and signup["data"]["route"] == "/user/goal-setup":
        ok("signup redirects to goal-setup")
    else:
        bad(f"signup route: {signup}")

    sel = handle_goal_selection(page, "General Fitness")
    if sel["success"] and sel["data"]["route"] == "/user/plan-preview":
        ok("goal selection -> plan-preview")
    else:
        bad("goal selection")

    start = handle_start_plan(page)
    if start["success"] and start["data"]["route"] == "/user/dashboard":
        ok("start plan -> dashboard")
    else:
        bad(f"start plan: {start}")

    uid = get_current_user_id(page)
    if route_guard(page, "/user/dashboard") == "/user/dashboard":
        ok("user with plan stays on dashboard")
    else:
        bad("dashboard guard with active plan")

    change = handle_change_plan(page)
    if change["success"] and change["data"]["route"] == "/user/change-plan":
        ok("change plan -> /user/change-plan")
    else:
        bad(f"change plan route: {change}")

    if route_guard(page, "/user/change-plan") == "/user/change-plan":
        ok("change-plan route allowed for user")
    else:
        bad("change-plan guard")

    # Admin login routing
    clear_current_user(page)
    admin_login = handle_login(page, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    if admin_login["success"] and admin_login["data"]["route"] == "/admin/dashboard":
        ok("admin login -> /admin/dashboard")
    else:
        bad("admin login route")

    if route_guard(page, "/user/dashboard") == "/admin/dashboard":
        ok("admin blocked from user dashboard")
    else:
        bad("admin user route block")

    # Admin data surfaces (no crash)
    try:
        admin_dashboard_content("Admin")
        leaderboard_content()
        reports_content()
        get_leaderboard()
        get_reports_summary()
        get_all_users(search="", status_filter="All Users")
        ok("admin dashboard/leaderboard/reports/users load")
    except Exception as exc:
        bad(f"admin surfaces: {exc}")

    # Logout
    logout = handle_logout(page)
    if logout["success"] and logout["data"]["route"] == "/login" and not is_logged_in(page):
        ok("logout clears session")
    else:
        bad("logout")

    if route_guard(page, "/user/dashboard") == "/login":
        ok("protected route after logout -> login")
    else:
        bad("post-logout guard")

    # Date formatting safety (demo crash guard)
    if format_date("2026-05-28 10:30:00") == "2026-05-28" and format_datetime("2026-05-28 10:30:00")[:16] == "2026-05-28 10:30":
        ok("safe date formatting")
    else:
        bad("date formatting")

    # All user routes resolve for logged-in user with plan
    handle_login(page, email, "Testpass1")
    for route in sorted(USER_ROUTES):
        page.route = route
        safe = route_guard(page, route)
        try:
            resolve_view(page, safe)
            ok(f"resolve user route {route}")
        except Exception as exc:
            bad(f"resolve user route {route}: {exc}")

    # Completed plan activity state
    from services.plan_service import start_new_plan
    from services.progress_service import complete_current_day

    uid = get_current_user_id(page)
    flex_gid = start_new_plan(uid, "Improve Flexibility")
    done = False
    while not done:
        current = [d for d in get_workout_days(flex_gid) if d["is_unlocked"] and not d["is_completed"]]
        if not current:
            break
        _, _, done = _complete_day_with_timer(uid, flex_gid, int(current[0]["id"]))
    if get_latest_completed_goal(uid):
        ok("latest completed goal available for activity page")
    else:
        bad("latest completed goal missing")

    # All admin routes resolve
    handle_login(page, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD)
    for route in sorted(ADMIN_ROUTES):
        page.route = route
        safe = route_guard(page, route)
        try:
            resolve_view(page, safe)
            ok(f"resolve admin route {route}")
        except Exception as exc:
            bad(f"resolve admin route {route}: {exc}")

    # Timeline generation sanity for every goal
    from models.goal_model import GOAL_DURATIONS

    for goal, duration in GOAL_DURATIONS.items():
        days = generate_plan_days(goal, duration)
        unlocked = sum(1 for d in days if d["is_unlocked"])
        if len(days) == duration and unlocked == 1:
            ok(f"plan generation {goal}")
        else:
            bad(f"plan generation {goal}")

    clear_current_user(page)
    _cleanup_test_user(email)


def test_duplicate_signup() -> None:
    from services.auth_service import create_user

    email = f"phase9.dup.{int(time.time())}@gymbro.test"
    _cleanup_test_user(email)
    ok1, _ = create_user("Dup", email, "Testpass1")
    ok2, msg2 = create_user("Dup2", email, "Testpass1")
    if ok1 and not ok2:
        ok("duplicate email blocked")
    else:
        bad(f"duplicate signup: ok2={ok2} msg={msg2}")
    _cleanup_test_user(email)


def main() -> int:
    print("=== Phase 9 Stability Validation ===\n")
    print("[1] Imports")
    test_imports()
    print("\n[2] Requirements")
    test_requirements()
    print("\n[3] Database")
    test_database()
    print("\n[4] Route protection")
    test_route_guard()
    print("\n[5] Auth validation")
    test_auth_validation()
    print("\n[6] Goal durations")
    test_goal_durations()
    print("\n[7] User flow (signup/plan/complete/change)")
    test_user_flow()
    print("\n[7b] Timer and timeline")
    test_timer_and_timeline()
    print("\n[8] Admin stats")
    test_admin_stats()
    print("\n[9] Duplicate signup")
    test_duplicate_signup()
    print("\n[10] Final demo regression")
    test_regression_demo()

    print(f"\n=== Results: {len(PASS)} passed, {len(FAIL)} failed ===")
    if FAIL:
        for item in FAIL:
            print(f"  - {item}")
        return 1
    print("\n=== ALL PHASE 9 CHECKS PASSED ===")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
