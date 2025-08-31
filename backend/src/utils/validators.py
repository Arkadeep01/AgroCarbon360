## backend/src/utils/validators.py

import re

def is_valid_email(email: str) -> bool:
    """Validates an email address using regex."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_phone_number(phone_number: str) -> bool:
    """Validates a phone number (simple validation for 10-15 digits)."""
    phone_regex = r'^\+?\d{10,15}$'
    return re.match(phone_regex, phone_number) is not None

def is_strong_password(password: str) -> bool:
    """Checks if a password is strong enough (at least 8 characters, including letters and numbers)."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True