from __future__ import annotations

from typing import Any


def success_response(message: str = "", data: Any = None) -> dict:
    return {"success": True, "message": message, "data": data, "errors": []}


def error_response(message: str = "", errors: list | None = None) -> dict:
    return {"success": False, "message": message, "data": None, "errors": errors or ([message] if message else [])}
