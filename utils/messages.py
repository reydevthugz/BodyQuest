"""Presentation-ready user-facing messages."""

# Auth
LOGIN_INVALID = "Invalid email or password."
SIGNUP_EMAIL_EXISTS = "This email is already registered."
SIGNUP_SUCCESS = "Account created successfully. Let's set your fitness goal."
ACCESS_DENIED = "You do not have permission to access this page."
GENERIC_ERROR = "Something went wrong while loading your data."
ACTIVITY_ERROR = "Unable to complete activity right now. Please try again."
ACTIVITY_LOCKED = "This task is locked."
ACTIVITY_ALREADY_DONE = "This task is already completed."
TASK_LOCKED = "Complete the current task first to unlock this day."
TIMER_REQUIRED = "Start your timer before completing this task."
SESSION_EXPIRED = "Please log in again."
PLAN_ERROR = "Unable to update your plan right now. Please try again."

# Plans & activity
PLAN_READY = "Your BodyQuest plan is ready. Day 1 is now available."
TASK_STARTED = "Task started. Stay focused."
TASK_COMPLETED = "Great job! Your task was completed."
ACTIVITY_UNLOCKED = "The next task is now unlocked."
NEXT_DAY_UNLOCKED = "The next task is now unlocked."
PLAN_COMPLETED = "Congratulations! You completed your BodyQuest goal."
WEEKLY_TASK_PROGRESS = "You completed your weekly task progress."
WEEKLY_CONSISTENCY = WEEKLY_TASK_PROGRESS
CHANGE_PLAN_SAVED = "Your previous progress was saved to Workout History."
CHANGE_PLAN_CONFIRM = (
    "Changing your plan will replace your active goal. "
    "Your completed tasks will stay in Workout History."
)

# User empty states
NO_ACTIVE_PLAN_FOUND = "No active plan found."
CHOOSE_GOAL_JOURNEY = "Choose a fitness goal to start your BodyQuest journey."
NO_ACTIVE_PLAN = CHOOSE_GOAL_JOURNEY
TASK_STOPPED = "Task stopped. You can resume anytime."
NO_ACHIEVEMENTS = "No achievements yet. Complete your first activity to earn one."
NO_WORKOUT_HISTORY = "No workout history yet. Complete your first activity to start tracking progress."

# Admin empty states
NO_REGISTERED_USERS = "No registered users yet."
NO_ACHIEVEMENTS_ADMIN = "No achievements recorded yet."
NO_WORKOUT_HISTORY_ADMIN = "No workout history available yet."
NO_ACTIVE_PLANS = "No active fitness plans yet."
NO_REPORT_DATA = "No report data available yet."
NO_LEADERBOARD = "Leaderboard will appear after users earn progress and achievements."


def day_unlocked_message(day_number: int) -> str:
    return f"Great job! Day {int(day_number)} is now unlocked."
