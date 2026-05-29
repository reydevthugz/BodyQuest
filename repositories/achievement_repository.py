from __future__ import annotations

from database.connection import get_connection
from utils.security import sanitize_like_pattern


class AchievementRepository:
    def achievement_exists(self, user_id: int, goal_id: int | None, name: str) -> bool:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            if goal_id is None:
                cur.execute(
                    "SELECT id FROM achievements WHERE user_id = %s AND goal_id IS NULL AND name = %s LIMIT 1",
                    (user_id, name),
                )
            else:
                cur.execute(
                    "SELECT id FROM achievements WHERE user_id = %s AND goal_id = %s AND name = %s LIMIT 1",
                    (user_id, goal_id, name),
                )
            return cur.fetchone() is not None

    def create_achievement(
        self,
        user_id: int,
        goal_id: int | None,
        name: str,
        description: str,
        badge_type: str,
    ) -> bool:
        if self.achievement_exists(user_id, goal_id, name):
            return False
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                INSERT INTO achievements (user_id, goal_id, name, description, badge_type)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, goal_id, name, description, badge_type),
            )
            conn.commit()
            return True

    def get_user_achievements(self, user_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT a.*, ug.goal_type
                FROM achievements a
                LEFT JOIN user_goals ug ON ug.id = a.goal_id
                WHERE a.user_id = %s
                ORDER BY a.earned_at DESC, a.id DESC
                """,
                (user_id,),
            )
            return cur.fetchall()

    def get_recent_user_achievements(self, user_id: int, limit: int = 5):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT a.*, ug.goal_type
                FROM achievements a
                LEFT JOIN user_goals ug ON ug.id = a.goal_id
                WHERE a.user_id = %s
                ORDER BY a.earned_at DESC, a.id DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            return cur.fetchall()

    def get_all_achievements(self, search: str | None = None, badge_type: str | None = None):
        query = """
            SELECT a.*, u.full_name, u.email, ug.goal_type
            FROM achievements a
            JOIN users u ON u.id = a.user_id
            LEFT JOIN user_goals ug ON ug.id = a.goal_id
            WHERE u.role = 'user'
        """
        params: list = []
        if search:
            query += " AND (u.full_name LIKE %s OR a.name LIKE %s)"
            pattern = sanitize_like_pattern(search)
            params.extend([pattern, pattern])
        if badge_type and badge_type != "All":
            query += " AND a.badge_type = %s"
            params.append(badge_type)
        query += " ORDER BY a.earned_at DESC, a.id DESC"
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(query, tuple(params))
            return cur.fetchall()
