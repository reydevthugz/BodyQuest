from __future__ import annotations

from repositories.admin_repository import AdminRepository
from repositories.achievement_repository import AchievementRepository
from repositories.goal_repository import GoalRepository
from repositories.progress_repository import ProgressRepository
from repositories.user_repository import UserRepository

_admin_repo = AdminRepository()
_user_repo = UserRepository()
_goal_repo = GoalRepository()
_achievement_repo = AchievementRepository()
_progress_repo = ProgressRepository()


def get_total_users() -> int:
    return _admin_repo.get_total_users()


def get_active_users_count() -> int:
    return _admin_repo.get_active_users_count()


def get_completed_goals_count() -> int:
    return _admin_repo.get_completed_goals_count()


def get_total_achievements_count() -> int:
    return _admin_repo.get_total_achievements_count()


def get_plans_in_progress_count() -> int:
    return _admin_repo.get_plans_in_progress_count()


def get_changed_plans_count() -> int:
    return _admin_repo.get_changed_plans_count()


def get_recent_user_activity(limit: int = 10):
    return _progress_repo.get_recent_user_activity(limit)


def get_goal_distribution():
    return _admin_repo.get_goal_distribution()


def get_top_performing_users(limit: int = 10):
    return _admin_repo.get_top_performing_users(limit)


def get_all_users(search: str | None = None, status_filter: str | None = None):
    from requests.admin_request import validate_badge_filter, validate_status_filter, validate_user_search

    safe_search = validate_user_search(search)
    safe_filter = validate_status_filter(status_filter)
    return _admin_repo.get_all_users(safe_search, safe_filter)


def get_user_details(user_id: int):
    return _user_repo.get_user_details(user_id)


def get_user_current_goal(user_id: int):
    return _goal_repo.get_user_current_goal(user_id)


def get_user_progress_summary(user_id: int):
    goal = get_user_current_goal(user_id)
    return _admin_repo.get_user_progress_summary(user_id, goal)


def get_user_achievements(user_id: int):
    return _achievement_repo.get_user_achievements(user_id)


def get_user_workout_history(user_id: int):
    return _progress_repo.get_admin_user_workout_history(user_id)


def get_all_achievements(search: str | None = None, badge_type: str | None = None):
    from requests.admin_request import validate_badge_filter, validate_user_search

    safe_search = validate_user_search(search)
    safe_badge = validate_badge_filter(badge_type)
    badge = None if safe_badge == "All" else safe_badge
    return _achievement_repo.get_all_achievements(safe_search, badge)


def get_leaderboard():
    return get_top_performing_users(limit=50)


def get_reports_summary():
    total_users = get_total_users()
    active_users = get_active_users_count()
    completed_goals = get_completed_goals_count()
    changed_plans = get_changed_plans_count()
    extra = _admin_repo.get_reports_extra()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "most_selected_goal": extra["top_goal"]["goal_type"] if extra["top_goal"] else "No data yet",
        "average_completion_progress": extra["avg_progress"],
        "completed_goals_count": completed_goals,
        "changed_plans_count": changed_plans,
        "most_earned_achievement": extra["top_achievement"]["name"] if extra["top_achievement"] else "No data yet",
        "recently_active_users": get_recent_user_activity(limit=5),
        "total_workout_days_completed": extra["completed_workouts"],
        "total_active_plans": extra["active_plans"],
        "total_completed_plans": extra["completed_plans"],
        "total_replaced_plans": extra["replaced_plans"],
    }


def get_dashboard_stats():
    return {
        "total_users": get_total_users(),
        "active_users": get_active_users_count(),
        "completed_goals": get_completed_goals_count(),
        "total_achievements": get_total_achievements_count(),
        "plans_in_progress": get_plans_in_progress_count(),
        "changed_plans": get_changed_plans_count(),
        "recent_user_activity": get_recent_user_activity(10),
        "goal_distribution": get_goal_distribution(),
        "top_performing_users": get_top_performing_users(10),
    }
