def format_percentage(value: float | int) -> str:
    return f"{int(round(value))}%"


def truncate_text(text: str, max_len: int = 80) -> str:
    text = text or ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def safe_text(value, default: str = "-") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default
