from __future__ import annotations

from datetime import datetime

from database.connection import get_connection


class GoalRepository:
    def create_goal(self, user_id: int, goal_type: str, duration: int) -> int:
        # Prevent duplicate active plans for the same user.
        self.mark_active_goal_replaced(int(user_id))
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                INSERT INTO user_goals (user_id, goal_type, plan_duration, difficulty_level, status)
                VALUES (%s, %s, %s, 'Beginner', 'active')
                """,
                (user_id, goal_type, duration),
            )
            conn.commit()
            return int(cur.lastrowid)

    def get_latest_completed_goal(self, user_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, user_id, goal_type, plan_duration, difficulty_level, status, completed_at
                FROM user_goals
                WHERE user_id = %s AND status = 'completed'
                ORDER BY completed_at DESC, id DESC
                LIMIT 1
                """,
                (int(user_id),),
            )
            return cur.fetchone()

    def get_active_goal(self, user_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, user_id, goal_type, plan_duration, difficulty_level, status, created_at
                FROM user_goals
                WHERE user_id = %s AND status = 'active'
                ORDER BY id DESC
                LIMIT 1
                """,
                (user_id,),
            )
            return cur.fetchone()

    def has_active_goal(self, user_id: int) -> bool:
        return self.get_active_goal(user_id) is not None

    def get_goal_by_id(self, goal_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM user_goals WHERE id = %s", (goal_id,))
            return cur.fetchone()

    def get_user_current_goal(self, user_id: int):
        return self.get_active_goal(user_id)

    def mark_active_goal_replaced(self, user_id: int) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                UPDATE user_goals
                SET status = 'replaced', replaced_at = %s
                WHERE user_id = %s AND status = 'active'
                """,
                (datetime.now(), user_id),
            )
            conn.commit()
            return int(cur.rowcount or 0)

    def mark_goal_completed(self, goal_id: int) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                UPDATE user_goals
                SET status = 'completed', completed_at = %s
                WHERE id = %s AND status = 'active'
                """,
                (datetime.now(), goal_id),
            )
            conn.commit()

    def is_goal_completed(self, goal_id: int) -> bool:
        goal = self.get_goal_by_id(goal_id)
        return bool(goal) and goal["status"] == "completed"

    def get_goal_type_and_duration(self, goal_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT goal_type, plan_duration FROM user_goals WHERE id = %s",
                (goal_id,),
            )
            return cur.fetchone() or {}

    def goal_belongs_to_user(self, goal_id: int, user_id: int) -> bool:
        goal = self.get_goal_by_id(goal_id)
        return bool(goal) and int(goal.get("user_id") or 0) == int(user_id)

    def get_active_goal_for_user(self, user_id: int, goal_id: int):
        goal = self.get_goal_by_id(goal_id)
        if not goal or int(goal.get("user_id") or 0) != int(user_id):
            return None
        if goal.get("status") != "active":
            return None
        return goal

    def count_active_goals(self, user_id: int) -> int:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT COUNT(*) AS total FROM user_goals WHERE user_id = %s AND status = 'active'",
                (int(user_id),),
            )
            row = cur.fetchone()
            return int(row["total"]) if row else 0
