"""
Seed only the default system administrator account (hashed password).

Rules:
- Never create demo/sample normal users
- Never seed fake plans, workouts, or achievements
- Never duplicate the admin if it already exists
- Never delete or modify existing user data
- Legacy admin@gymbro.com is left untouched if it already exists
"""

from config.settings import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASSWORD
from repositories.user_repository import UserRepository


def seed_default_admin() -> bool:
    """
    Ensure the default BodyQuest admin exists. Returns True if a new admin was created.
    Does not modify or remove legacy admin@gymbro.com accounts.
    """
    repo = UserRepository()
    if repo.find_by_email(DEFAULT_ADMIN_EMAIL):
        return False
    repo.create_user(
        full_name=DEFAULT_ADMIN_NAME,
        email=DEFAULT_ADMIN_EMAIL,
        plain_password=DEFAULT_ADMIN_PASSWORD,
        role="admin",
    )
    return True
