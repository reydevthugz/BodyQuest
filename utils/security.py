from __future__ import annotations

import hashlib
import hmac
import re
import secrets

PBKDF2_ITERATIONS = 260_000
SALT_BYTES = 32
MAX_TEXT_LENGTH = 150
MAX_SEARCH_LENGTH = 100
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def generate_salt() -> str:
    return secrets.token_hex(SALT_BYTES)


def hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return digest.hex()


def verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    if not password or not stored_hash or not stored_salt:
        return False
    try:
        computed = hash_password(password, stored_salt)
        return hmac.compare_digest(computed, stored_hash)
    except (ValueError, TypeError):
        return False


def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit


def sanitize_text(value: str, max_length: int = MAX_TEXT_LENGTH) -> str:
    text = (value or "").strip()
    if len(text) > max_length:
        text = text[:max_length]
    return text


def normalize_email(email: str) -> str:
    return sanitize_text(email, max_length=150).lower()


def is_valid_email(email: str) -> bool:
    if not email or len(email) > 150:
        return False
    return bool(EMAIL_PATTERN.match(email))


def sanitize_like_pattern(search: str, max_length: int = MAX_SEARCH_LENGTH) -> str:
    """Escape LIKE wildcards in user search terms."""
    cleaned = sanitize_text(search, max_length=max_length)
    cleaned = cleaned.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{cleaned}%"
