from __future__ import annotations

from database.connection import get_connection
from utils.security import generate_salt, hash_password, normalize_email, sanitize_text
from utils.validators import is_allowed_role


class UserRepository:
    def find_by_email(self, email: str):
        email = normalize_email(email)
        if not email:
            return None
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, full_name, email, role, password, password_hash, password_salt
                FROM users WHERE email = %s
                """,
                (email,),
            )
            return cur.fetchone()

    def find_by_id(self, user_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, full_name, email, role FROM users WHERE id = %s",
                (int(user_id),),
            )
            return cur.fetchone()

    def email_exists(self, email: str) -> bool:
        return self.find_by_email(email) is not None

    def create_user(self, full_name: str, email: str, plain_password: str, role: str = "user") -> int:
        if not is_allowed_role(role):
            raise ValueError("Invalid role.")
        full_name = sanitize_text(full_name)
        email = normalize_email(email)
        salt = generate_salt()
        pwd_hash = hash_password(plain_password, salt)
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                INSERT INTO users (full_name, email, password, password_hash, password_salt, role)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (full_name, email, "", pwd_hash, salt, role),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_password_hash(self, user_id: int, password_hash: str, password_salt: str) -> None:
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                UPDATE users
                SET password_hash = %s, password_salt = %s, password = %s
                WHERE id = %s
                """,
                (password_hash, password_salt, "", int(user_id)),
            )
            conn.commit()

    def get_user_details(self, user_id: int):
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, full_name, email, role, created_at FROM users WHERE id = %s AND role = 'user'",
                (int(user_id),),
            )
            return cur.fetchone()
