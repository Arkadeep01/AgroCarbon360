# backend/src/utils/helpers.py
import uuid
import random
import string
from datetime import datetime
from typing import Optional

# ---------------------------
# General Utility Helpers
# ---------------------------

def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


def generate_random_string(length: int = 12) -> str:
    """Generate a random alphanumeric string of given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_current_timestamp() -> str:
    """Return current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def mask_email(email: str) -> str:
    """Mask an email address (for logging or displaying safely)."""
    try:
        local, domain = email.split("@")
        return local[0] + "***@" + domain
    except Exception:
        return "***invalid_email***"


def safe_get(obj: dict, key: str, default: Optional[str] = None):
    """Safely fetch a key from a dict with default fallback."""
    return obj.get(key, default)


# ---------------------------
# Domain-Specific Helpers
# ---------------------------

def calculate_carbon_savings(acreage: float, crop_type: str) -> float:
    """
    Example helper for AgroCarbon360 domain.
    Dummy logic for now – replace with real formula later.
    """
    crop_factor = {
        "rice": 1.2,
        "wheat": 0.8,
        "maize": 1.0,
    }
    factor = crop_factor.get(crop_type.lower(), 1.0)
    return round(acreage * factor * 0.5, 2)


def format_response_message(action: str, success: bool = True) -> str:
    """Format standardized response messages."""
    status = "succeeded" if success else "failed"
    return f"Action '{action}' {status} at {get_current_timestamp()}"
