from __future__ import annotations

from datetime import datetime

from database.connection import get_connection


class WorkoutRepository:
    def create_workout_days(self, goal_id: int, plan_days: list[dict]) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            for day in plan_days:
                status = day.get("status") or ("current" if day.get("is_unlocked") else "locked")
                cur.execute(
                    """
                    INSERT INTO workout_days (
                        goal_id, day_number, title, warmup, main_activity, cooldown, safety_tip,
                        estimated_minutes, is_unlocked, is_completed, status, selected_as_today
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        goal_id,
                        day["day_number"],
                        day["title"],
                        day["warmup"],
                        day["main_activity"],
                        day["cooldown"],
                        day["safety_tip"],
                        day["estimated_minutes"],
                        day["is_unlocked"],
                        day["is_completed"],
                        status,
                        day.get("day_number") == 1,
                    ),
                )
            conn.commit()

    def get_workout_days(self, goal_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT * FROM workout_days
                WHERE goal_id = %s
                ORDER BY day_number ASC
                """,
                (goal_id,),
            )
            return cur.fetchall()

    def get_workout_day(self, workout_day_id: int, goal_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM workout_days WHERE id = %s AND goal_id = %s",
                (int(workout_day_id), int(goal_id)),
            )
            return cur.fetchone()

    def get_current_unlocked_day_for_goal(self, goal_id: int):
        return self.get_current_unlocked_day(goal_id)

    def get_current_unlocked_day(self, goal_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT * FROM workout_days
                WHERE goal_id = %s AND is_unlocked = TRUE AND is_completed = FALSE
                ORDER BY day_number ASC
                LIMIT 1
                """,
                (goal_id,),
            )
            return cur.fetchone()

    def get_selected_day(self, goal_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT * FROM workout_days
                WHERE goal_id = %s AND selected_as_today = TRUE
                LIMIT 1
                """,
                (goal_id,),
            )
            return cur.fetchone()

    def get_completed_days_count(self, goal_id: int) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT COUNT(*) AS total FROM workout_days WHERE goal_id = %s AND is_completed = TRUE",
                (goal_id,),
            )
            row = cur.fetchone()
            return int(row["total"]) if row else 0

    def mark_day_started(self, workout_day_id: int) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                UPDATE workout_days
                SET started_at = %s, status = 'in_progress'
                WHERE id = %s AND is_completed = FALSE
                """,
                (datetime.now(), workout_day_id),
            )
            conn.commit()

    def mark_day_completed(self, workout_day_id: int, actual_duration_seconds: int = 0) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                UPDATE workout_days
                SET is_completed = TRUE,
                    completed_at = %s,
                    status = 'completed',
                    actual_duration_seconds = %s,
                    selected_as_today = FALSE
                WHERE id = %s
                """,
                (datetime.now(), int(actual_duration_seconds or 0), workout_day_id),
            )
            conn.commit()

    def unlock_next_day(self, goal_id: int, current_day_number: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, day_number FROM workout_days
                WHERE goal_id = %s AND day_number = %s
                LIMIT 1
                """,
                (goal_id, current_day_number + 1),
            )
            next_day = cur.fetchone()
            if not next_day:
                return None
            cur.execute(
                """
                UPDATE workout_days
                SET is_unlocked = TRUE, status = 'current', selected_as_today = TRUE
                WHERE id = %s
                """,
                (next_day["id"],),
            )
            cur.execute(
                "UPDATE workout_days SET selected_as_today = FALSE WHERE goal_id = %s AND id != %s",
                (goal_id, next_day["id"]),
            )
            conn.commit()
            cur.execute("SELECT * FROM workout_days WHERE id = %s", (next_day["id"],))
            return cur.fetchone()

    def set_selected_day(self, goal_id: int, workout_day_id: int) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "UPDATE workout_days SET selected_as_today = FALSE WHERE goal_id = %s",
                (goal_id,),
            )
            cur.execute(
                "UPDATE workout_days SET selected_as_today = TRUE WHERE id = %s AND goal_id = %s",
                (workout_day_id, goal_id),
            )
            conn.commit()

    def clear_selected_day(self, goal_id: int) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "UPDATE workout_days SET selected_as_today = FALSE WHERE goal_id = %s",
                (goal_id,),
            )
            conn.commit()

    def count_completed_for_goal(self, goal_id: int) -> int:
        return self.get_completed_days_count(goal_id)
