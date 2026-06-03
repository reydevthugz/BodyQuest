from __future__ import annotations

from mysql.connector import Error

from config.settings import DB_NAME
from database.connection import _base_connection


def _column_exists(cur, table: str, column: str) -> bool:
    cur.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (DB_NAME, table, column),
    )
    row = cur.fetchone()
    return bool(row and int(row["total"]) > 0)


def _add_column_if_missing(cur, table: str, column: str, definition: str) -> None:
    if _column_exists(cur, table, column):
        return
    try:
        cur.execute(f"ALTER TABLE `{table}` ADD COLUMN {column} {definition}")
    except Error as exc:
        # MySQL 1060: column already exists (schema drift / partial migration).
        if getattr(exc, "errno", None) != 1060:
            raise


def _ensure_user_password_columns(cur) -> None:
    _add_column_if_missing(cur, "users", "password_hash", "VARCHAR(255) NULL")
    _add_column_if_missing(cur, "users", "password_salt", "VARCHAR(255) NULL")


def _ensure_workout_day_columns(cur) -> None:
    _add_column_if_missing(cur, "workout_days", "description", "TEXT NULL")
    _add_column_if_missing(cur, "workout_days", "status", "VARCHAR(50) DEFAULT 'locked'")
    _add_column_if_missing(cur, "workout_days", "started_at", "DATETIME NULL")
    _add_column_if_missing(cur, "workout_days", "actual_duration_seconds", "INT DEFAULT 0")
    _add_column_if_missing(cur, "workout_days", "selected_as_today", "BOOLEAN DEFAULT FALSE")
    _add_column_if_missing(cur, "progress_logs", "duration_seconds", "INT DEFAULT 0")
    cur.execute("UPDATE workout_days SET status = 'completed' WHERE is_completed = TRUE")
    cur.execute(
        "UPDATE workout_days SET status = 'in_progress' WHERE started_at IS NOT NULL AND is_completed = FALSE"
    )
    cur.execute(
        """
        UPDATE workout_days SET status = 'current'
        WHERE is_unlocked = TRUE AND is_completed = FALSE AND (started_at IS NULL OR status != 'in_progress')
        """
    )
    cur.execute(
        "UPDATE workout_days SET status = 'locked' WHERE is_completed = FALSE AND is_unlocked = FALSE"
    )


def initialize_database() -> None:
    conn = None
    try:
        conn = _base_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        cur.execute(f"USE `{DB_NAME}`")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL DEFAULT '',
                password_hash VARCHAR(255) NULL,
                password_salt VARCHAR(255) NULL,
                role ENUM('admin','user') DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _ensure_user_password_columns(cur)

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS user_goals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                goal_type VARCHAR(100) NOT NULL,
                plan_duration INT NOT NULL,
                difficulty_level VARCHAR(50) DEFAULT 'Beginner',
                status ENUM('active','completed','replaced') DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME NULL,
                replaced_at DATETIME NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_days (
                id INT AUTO_INCREMENT PRIMARY KEY,
                goal_id INT NOT NULL,
                day_number INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                warmup TEXT,
                main_activity TEXT,
                cooldown TEXT,
                safety_tip TEXT,
                estimated_minutes INT DEFAULT 20,
                is_unlocked BOOLEAN DEFAULT FALSE,
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at DATETIME NULL,
                FOREIGN KEY (goal_id) REFERENCES user_goals(id) ON DELETE CASCADE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS progress_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                goal_id INT NULL,
                workout_day_id INT NULL,
                action VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (goal_id) REFERENCES user_goals(id) ON DELETE SET NULL,
                FOREIGN KEY (workout_day_id) REFERENCES workout_days(id) ON DELETE SET NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS achievements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                goal_id INT NULL,
                name VARCHAR(150) NOT NULL,
                description TEXT,
                badge_type VARCHAR(100),
                earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (goal_id) REFERENCES user_goals(id) ON DELETE SET NULL
            )
            """
        )
        _ensure_workout_day_columns(cur)
        conn.commit()
    except Error as exc:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Database initialization failed: {exc}") from exc
    finally:
        if conn and conn.is_connected():
            conn.close()
