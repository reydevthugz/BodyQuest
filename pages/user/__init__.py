from pages.user.activity import activity_view
from pages.user.achievements import achievements_view
from pages.user.dashboard import dashboard_view
from pages.user.goal_setup import goal_setup_view
from pages.user.history import history_view
from pages.user.plan_preview import plan_preview_view
from pages.user.profile import profile_view
from pages.user.timeline import timeline_view


def user_view(page):
    route = page.route
    if route == "/user/dashboard":
        return dashboard_view(page)
    if route in ("/user/goal-setup", "/user/change-plan"):
        return goal_setup_view(page)
    if route == "/user/plan-preview":
        return plan_preview_view(page)
    if route == "/user/activity":
        return activity_view(page)
    if route == "/user/timeline":
        return timeline_view(page)
    if route == "/user/achievements":
        return achievements_view(page)
    if route == "/user/history":
        return history_view(page)
    if route == "/user/profile":
        return profile_view(page)
    return dashboard_view(page)


__all__ = [
    "user_view",
    "dashboard_view",
    "goal_setup_view",
    "plan_preview_view",
    "activity_view",
    "timeline_view",
    "achievements_view",
    "history_view",
    "profile_view",
]
