from __future__ import annotations

from services import achievement_service


def get_user_achievements_data(user_id: int):
    return achievement_service.get_user_achievements(user_id)
