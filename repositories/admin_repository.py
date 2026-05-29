from __future__ import annotations

from database.connection import get_connection
from utils.security import sanitize_like_pattern


class AdminRepository:
    def get_total_users(self) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'user'")
            row = cur.fetchone() or {"total": 0}
            return int(row["total"])

    def get_active_users_count(self) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT COUNT(DISTINCT u.id) AS total
                FROM users u
                JOIN user_goals ug ON ug.user_id = u.id AND ug.status = 'active'
                WHERE u.role = 'user'
                """
            )
            row = cur.fetchone() or {"total": 0}
            return int(row["total"])

    def get_completed_goals_count(self) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM user_goals ug
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user' AND ug.status = 'completed'
                """
            )
            row = cur.fetchone() or {"total": 0}
            return int(row["total"])

    def get_total_achievements_count(self) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM achievements a
                JOIN users u ON u.id = a.user_id
                WHERE u.role = 'user'
                """
            )
            row = cur.fetchone() or {"total": 0}
            return int(row["total"])

    def get_plans_in_progress_count(self) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM user_goals ug
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user' AND ug.status = 'active'
                """
            )
            row = cur.fetchone() or {"total": 0}
            return int(row["total"])

    def get_changed_plans_count(self) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM user_goals ug
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user' AND ug.status = 'replaced'
                """
            )
            row = cur.fetchone() or {"total": 0}
            return int(row["total"])

    def get_goal_distribution(self):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT ug.goal_type, COUNT(*) AS total
                FROM user_goals ug
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user'
                GROUP BY ug.goal_type
                ORDER BY total DESC
                """
            )
            rows = cur.fetchall()
        grand = sum(int(r["total"]) for r in rows) or 1
        return [
            {
                "goal_type": r["goal_type"],
                "total": int(r["total"]),
                "ratio": int(round((int(r["total"]) / grand) * 100)),
            }
            for r in rows
        ]

    def get_top_performing_users(self, limit: int = 10):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT
                    u.id,
                    u.full_name,
                    u.email,
                    COALESCE(ach.total_achievements, 0) AS total_achievements,
                    COALESCE(goals.completed_goals, 0) AS completed_goals,
                    COALESCE(w.completed_days, 0) AS completed_workout_days,
                    active.goal_type AS current_goal,
                    CASE
                        WHEN active.plan_duration IS NULL OR active.plan_duration = 0 THEN 0
                        ELSE ROUND((COALESCE(active.completed_days, 0) / active.plan_duration) * 100)
                    END AS current_progress
                FROM users u
                LEFT JOIN (
                    SELECT user_id, COUNT(*) AS total_achievements
                    FROM achievements
                    GROUP BY user_id
                ) ach ON ach.user_id = u.id
                LEFT JOIN (
                    SELECT user_id, COUNT(*) AS completed_goals
                    FROM user_goals
                    WHERE status = 'completed'
                    GROUP BY user_id
                ) goals ON goals.user_id = u.id
                LEFT JOIN (
                    SELECT ug.user_id, COUNT(*) AS completed_days
                    FROM workout_days wd
                    JOIN user_goals ug ON ug.id = wd.goal_id
                    WHERE wd.is_completed = TRUE
                    GROUP BY ug.user_id
                ) w ON w.user_id = u.id
                LEFT JOIN (
                    SELECT ug.user_id, ug.goal_type, ug.plan_duration,
                        (SELECT COUNT(*) FROM workout_days wd WHERE wd.goal_id = ug.id AND wd.is_completed = TRUE) AS completed_days
                    FROM user_goals ug
                    WHERE ug.status = 'active'
                ) active ON active.user_id = u.id
                WHERE u.role = 'user'
                ORDER BY total_achievements DESC, completed_goals DESC, completed_workout_days DESC, current_progress DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cur.fetchall()

    def get_all_users(self, search: str | None = None, status_filter: str | None = None):
        query = """
            SELECT
                u.id,
                u.full_name,
                u.email,
                u.created_at,
                active.goal_type AS current_goal,
                active.plan_duration,
                active.id AS active_goal_id,
                COALESCE(active.completed_days, 0) AS completed_days,
                COALESCE(active.progress_percent, 0) AS progress_percent,
                last_activity.last_activity_at,
                COALESCE(ach.total_achievements, 0) AS total_achievements,
                CASE
                    WHEN active.id IS NOT NULL THEN 'active'
                    WHEN completed_any.has_completed = 1 THEN 'completed_goal'
                    WHEN replaced_any.has_replaced = 1 THEN 'changed_plan'
                    ELSE 'inactive'
                END AS status_tag
            FROM users u
            LEFT JOIN (
                SELECT ug.user_id, ug.id, ug.goal_type, ug.plan_duration,
                    (SELECT COUNT(*) FROM workout_days wd WHERE wd.goal_id = ug.id AND wd.is_completed = TRUE) AS completed_days,
                    CASE
                        WHEN ug.plan_duration = 0 THEN 0
                        ELSE ROUND(((SELECT COUNT(*) FROM workout_days wd WHERE wd.goal_id = ug.id AND wd.is_completed = TRUE) / ug.plan_duration) * 100)
                    END AS progress_percent
                FROM user_goals ug
                WHERE ug.status = 'active'
            ) active ON active.user_id = u.id
            LEFT JOIN (
                SELECT user_id, MAX(created_at) AS last_activity_at
                FROM progress_logs
                GROUP BY user_id
            ) last_activity ON last_activity.user_id = u.id
            LEFT JOIN (
                SELECT user_id, COUNT(*) AS total_achievements
                FROM achievements
                GROUP BY user_id
            ) ach ON ach.user_id = u.id
            LEFT JOIN (
                SELECT user_id, 1 AS has_completed
                FROM user_goals
                WHERE status = 'completed'
                GROUP BY user_id
            ) completed_any ON completed_any.user_id = u.id
            LEFT JOIN (
                SELECT user_id, 1 AS has_replaced
                FROM user_goals
                WHERE status = 'replaced'
                GROUP BY user_id
            ) replaced_any ON replaced_any.user_id = u.id
            WHERE u.role = 'user'
        """
        params: list = []
        if search:
            query += " AND (u.full_name LIKE %s OR u.email LIKE %s)"
            pattern = sanitize_like_pattern(search)
            params.extend([pattern, pattern])
        if status_filter == "Active":
            query += " AND active.id IS NOT NULL"
        elif status_filter == "Inactive":
            query += " AND active.id IS NULL AND (last_activity.last_activity_at IS NULL OR last_activity.last_activity_at < DATE_SUB(NOW(), INTERVAL 14 DAY))"
        elif status_filter == "Completed Goal":
            query += " AND completed_any.has_completed = 1"
        elif status_filter == "Changed Plan":
            query += " AND replaced_any.has_replaced = 1"
        query += " ORDER BY u.created_at DESC, u.id DESC"
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(query, tuple(params))
            return cur.fetchall()

    def get_user_progress_summary(self, user_id: int, goal: dict | None):
        if not goal:
            return {
                "current_unlocked_day": None,
                "completed_days": 0,
                "remaining_days": 0,
                "progress_percent": 0,
                "last_completed_activity": None,
                "status": "inactive",
            }
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT COUNT(*) AS total FROM workout_days WHERE goal_id = %s AND is_completed = TRUE",
                (goal["id"],),
            )
            completed = int((cur.fetchone() or {"total": 0})["total"])
            cur.execute(
                """
                SELECT day_number, title, completed_at
                FROM workout_days
                WHERE goal_id = %s AND is_completed = TRUE
                ORDER BY completed_at DESC LIMIT 1
                """,
                (goal["id"],),
            )
            last_completed = cur.fetchone()
            cur.execute(
                """
                SELECT day_number
                FROM workout_days
                WHERE goal_id = %s AND is_unlocked = TRUE AND is_completed = FALSE
                ORDER BY day_number ASC LIMIT 1
                """,
                (goal["id"],),
            )
            unlocked = cur.fetchone()
        total = int(goal["plan_duration"] or 0)
        remaining = max(total - completed, 0)
        progress = round((completed / total) * 100) if total else 0
        return {
            "current_unlocked_day": int(unlocked["day_number"]) if unlocked else None,
            "completed_days": completed,
            "remaining_days": remaining,
            "progress_percent": progress,
            "last_completed_activity": last_completed,
            "status": "active",
        }

    def get_reports_extra(self):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT goal_type, COUNT(*) AS total
                FROM user_goals ug
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user'
                GROUP BY goal_type
                ORDER BY total DESC
                LIMIT 1
                """
            )
            top_goal = cur.fetchone()
            cur.execute(
                """
                SELECT ROUND(AVG(progress.progress_percent), 0) AS avg_progress
                FROM (
                    SELECT
                        ug.id,
                        CASE
                            WHEN ug.plan_duration = 0 THEN 0
                            ELSE ((SELECT COUNT(*) FROM workout_days wd WHERE wd.goal_id = ug.id AND wd.is_completed = TRUE) / ug.plan_duration) * 100
                        END AS progress_percent
                    FROM user_goals ug
                    JOIN users u ON u.id = ug.user_id
                    WHERE u.role = 'user'
                ) progress
                """
            )
            avg_progress = int((cur.fetchone() or {"avg_progress": 0})["avg_progress"] or 0)
            cur.execute(
                """
                SELECT a.name, COUNT(*) AS total
                FROM achievements a
                JOIN users u ON u.id = a.user_id
                WHERE u.role = 'user'
                GROUP BY a.name
                ORDER BY total DESC
                LIMIT 1
                """
            )
            top_achievement = cur.fetchone()
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM workout_days wd
                JOIN user_goals ug ON ug.id = wd.goal_id
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user' AND wd.is_completed = TRUE
                """
            )
            completed_workouts = int((cur.fetchone() or {"total": 0})["total"])
            cur.execute(
                """
                SELECT COUNT(*) AS total FROM user_goals ug
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user' AND ug.status = 'active'
                """
            )
            active_plans = int((cur.fetchone() or {"total": 0})["total"])
            cur.execute(
                """
                SELECT COUNT(*) AS total FROM user_goals ug
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user' AND ug.status = 'completed'
                """
            )
            completed_plans = int((cur.fetchone() or {"total": 0})["total"])
            cur.execute(
                """
                SELECT COUNT(*) AS total FROM user_goals ug
                JOIN users u ON u.id = ug.user_id
                WHERE u.role = 'user' AND ug.status = 'replaced'
                """
            )
            replaced_plans = int((cur.fetchone() or {"total": 0})["total"])
        return {
            "top_goal": top_goal,
            "avg_progress": avg_progress,
            "top_achievement": top_achievement,
            "completed_workouts": completed_workouts,
            "active_plans": active_plans,
            "completed_plans": completed_plans,
            "replaced_plans": replaced_plans,
        }
