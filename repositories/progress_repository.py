from __future__ import annotations

from database.connection import get_connection


class ProgressRepository:
    def log_exists(self, user_id: int, workout_day_id: int | None, action: str) -> bool:
        if workout_day_id is None:
            return False
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id FROM progress_logs
                WHERE user_id = %s AND workout_day_id = %s AND action = %s
                LIMIT 1
                """,
                (int(user_id), int(workout_day_id), action),
            )
            return cur.fetchone() is not None

    def add_log(
        self,
        user_id: int,
        goal_id: int | None,
        workout_day_id: int | None,
        action: str,
        duration_seconds: int = 0,
    ) -> None:
        if workout_day_id is not None and self.log_exists(user_id, workout_day_id, action):
            return
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                INSERT INTO progress_logs (user_id, goal_id, workout_day_id, action, duration_seconds)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, goal_id, workout_day_id, action, int(duration_seconds or 0)),
            )
            conn.commit()

    def get_user_workout_history(self, user_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT
                    wd.id AS workout_day_id,
                    wd.day_number,
                    wd.title,
                    wd.completed_at,
                    wd.actual_duration_seconds,
                    ug.id AS goal_id,
                    ug.goal_type,
                    ug.status AS plan_status
                FROM workout_days wd
                JOIN user_goals ug ON ug.id = wd.goal_id
                WHERE ug.user_id = %s AND wd.is_completed = TRUE
                ORDER BY wd.completed_at DESC, wd.id DESC
                """,
                (user_id,),
            )
            return cur.fetchall()

    def get_recent_workout_history(self, user_id: int, limit: int = 5):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT
                    wd.id AS workout_day_id,
                    wd.day_number,
                    wd.title,
                    wd.completed_at,
                    wd.actual_duration_seconds,
                    ug.id AS goal_id,
                    ug.goal_type,
                    ug.status AS plan_status
                FROM workout_days wd
                JOIN user_goals ug ON ug.id = wd.goal_id
                WHERE ug.user_id = %s AND wd.is_completed = TRUE
                ORDER BY wd.completed_at DESC, wd.id DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            return cur.fetchall()

    def get_admin_user_workout_history(self, user_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT wd.day_number, wd.title, wd.completed_at, wd.actual_duration_seconds,
                       ug.goal_type, ug.status AS plan_status
                FROM workout_days wd
                JOIN user_goals ug ON ug.id = wd.goal_id
                WHERE ug.user_id = %s AND wd.is_completed = TRUE
                ORDER BY wd.completed_at DESC, wd.id DESC
                """,
                (user_id,),
            )
            return cur.fetchall()

    def get_recent_user_activity(self, limit: int = 10):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT p.id, p.action, p.created_at, u.full_name, u.email, ug.goal_type
                FROM progress_logs p
                JOIN users u ON u.id = p.user_id
                LEFT JOIN user_goals ug ON ug.id = p.goal_id
                WHERE u.role = 'user'
                ORDER BY p.created_at DESC, p.id DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cur.fetchall()
