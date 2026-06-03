from __future__ import annotations

from datetime import datetime

from database.connection import get_connection


class WorkoutRepository:
    def _insert_plan_day(self, cur, goal_id: int, day: dict, include_description: bool = True) -> None:
        status = day.get("status") or ("current" if day.get("is_unlocked") else "locked")
        unlocked = 1 if day.get("is_unlocked") else 0
        completed = 1 if day.get("is_completed") else 0
        selected = 1 if day.get("day_number") == 1 else 0
        params = (
            goal_id,
            day["day_number"],
            day["title"],
            day.get("description") or day["main_activity"],
            day["warmup"],
            day["main_activity"],
            day["cooldown"],
            day["safety_tip"],
            day["estimated_minutes"],
            unlocked,
            completed,
            status,
            selected,
        )
        if include_description:
            cur.execute(
                """
                INSERT INTO workout_days (
                    goal_id, day_number, title, description, warmup, main_activity, cooldown,
                    safety_tip, estimated_minutes, is_unlocked, is_completed, status, selected_as_today
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                params,
            )
        else:
            cur.execute(
                """
                INSERT INTO workout_days (
                    goal_id, day_number, title, warmup, main_activity, cooldown,
                    safety_tip, estimated_minutes, is_unlocked, is_completed, status, selected_as_today
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
                    unlocked,
                    completed,
                    status,
                    selected,
                ),
            )

    def create_workout_days(self, goal_id: int, plan_days: list[dict]) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)

            def _insert_all(include_description: bool) -> None:
                for day in plan_days:
                    self._insert_plan_day(cur, goal_id, day, include_description=include_description)

            try:
                _insert_all(include_description=True)
                conn.commit()
            except Exception as exc:
                conn.rollback()
                if "description" not in str(exc).lower():
                    raise
                _insert_all(include_description=False)
                conn.commit()

    def count_workout_days(self, goal_id: int) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT COUNT(*) AS total FROM workout_days WHERE goal_id = %s",
                (int(goal_id),),
            )
            row = cur.fetchone()
            return int(row["total"]) if row else 0

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

    def mark_day_stopped(self, workout_day_id: int) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                UPDATE workout_days
                SET status = 'stopped'
                WHERE id = %s AND is_completed = FALSE
                """,
                (workout_day_id,),
            )
            conn.commit()

    def mark_day_resumed(self, workout_day_id: int) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                UPDATE workout_days
                SET status = 'in_progress'
                WHERE id = %s AND is_completed = FALSE
                """,
                (workout_day_id,),
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
