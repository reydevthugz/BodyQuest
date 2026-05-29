from __future__ import annotations

from repositories.achievement_repository import AchievementRepository
from repositories.goal_repository import GoalRepository
from repositories.workout_repository import WorkoutRepository

_achievement_repo = AchievementRepository()
_goal_repo = GoalRepository()
_workout_repo = WorkoutRepository()


def achievement_exists(user_id: int, goal_id: int | None, name: str) -> bool:
    return _achievement_repo.achievement_exists(user_id, goal_id, name)


def award_achievement(user_id: int, goal_id: int | None, name: str, description: str, badge_type: str) -> bool:
    return _achievement_repo.create_achievement(user_id, goal_id, name, description, badge_type)


def check_and_award_achievements(user_id: int, goal_id: int) -> None:
    completed = _workout_repo.count_completed_for_goal(goal_id)
    goal = _goal_repo.get_goal_type_and_duration(goal_id)
    goal_type = goal.get("goal_type")
    duration = int(goal.get("plan_duration") or 0)

    if completed >= 1:
        award_achievement(user_id, goal_id, "First Step Completed", "Completed your first workout day.", "starter")
    if completed >= 3:
        award_achievement(user_id, goal_id, "3-Day Streak", "Completed 3 workout days.", "streak")
    if completed >= 7:
        award_achievement(user_id, goal_id, "7-Day Consistency", "Completed 7 workout days.", "consistency")
    if goal_type in ("Lose Weight", "Improve Endurance"):
        award_achievement(user_id, goal_id, "Cardio Starter", "Started or progressed in a cardio-focused plan.", "cardio")
    if goal_type == "Gain Muscle":
        award_achievement(user_id, goal_id, "Strength Beginner", "Started or progressed in a muscle-focused plan.", "strength")
    if goal_type == "Improve Flexibility":
        award_achievement(user_id, goal_id, "Flexibility Builder", "Started or progressed in a flexibility-focused plan.", "flexibility")
    if duration and completed >= duration:
        award_achievement(user_id, goal_id, "Full Plan Champion", "Completed every day of your beginner plan.", "champion")


def get_user_achievements(user_id: int):
    return _achievement_repo.get_user_achievements(user_id)


def get_recent_user_achievements(user_id: int, limit: int = 5):
    return _achievement_repo.get_recent_user_achievements(user_id, limit)
