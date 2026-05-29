from __future__ import annotations

from utils.security import is_strong_password, is_valid_email, normalize_email, sanitize_text


def validate_login(email: str, password: str) -> dict:
    errors = []
    email = normalize_email(email)
    password = (password or "").strip()
    if not email:
        errors.append("Email is required.")
    elif not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not password:
        errors.append("Password is required.")
    return {"valid": not errors, "errors": errors, "email": email}


def validate_signup(full_name: str, email: str, password: str, confirm_password: str) -> dict:
    errors = []
    full_name = sanitize_text(full_name)
    email = normalize_email(email)
    password = (password or "").strip()
    confirm_password = (confirm_password or "").strip()

    if not full_name:
        errors.append("Full name is required.")
    if not email:
        errors.append("Email is required.")
    elif not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not password:
        errors.append("Password is required.")
    elif not is_strong_password(password):
        errors.append("Password must be at least 8 characters and include a letter and a number.")
    if not confirm_password:
        errors.append("Confirm password is required.")
    elif password != confirm_password:
        errors.append("Passwords do not match.")

    return {
        "valid": not errors,
        "errors": errors,
        "full_name": full_name,
        "email": email,
        "password": password,
    }
