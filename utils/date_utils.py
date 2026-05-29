from __future__ import annotations

from datetime import datetime


def get_current_datetime() -> datetime:
    return datetime.now()


def _coerce_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if hasattr(value, "strftime"):
        return value
    if isinstance(value, str):
        text = value.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(text[:19] if fmt.startswith("%Y-%m-%d %H") else text[:10], fmt)
            except ValueError:
                continue
    return None


def format_date(value) -> str:
    if not value:
        return "-"
    dt = _coerce_datetime(value)
    if dt:
        return dt.strftime("%Y-%m-%d")
    if isinstance(value, str) and len(value) >= 10:
        return value[:10]
    return str(value)


def format_datetime(value) -> str:
    if not value:
        return "-"
    dt = _coerce_datetime(value)
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, str) and len(value) >= 16:
        return value[:16]
    if isinstance(value, str) and len(value) >= 10:
        return value[:10]
    return str(value)
