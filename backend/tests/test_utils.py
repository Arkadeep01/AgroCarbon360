from src.utils.hashing import hash_password, verify_password
from src.utils.validators import is_valid_email
from src.utils.jwt_handler import create_access_token, decode_access_token

def test_hash_and_verify_password():
    pwd = "secret123"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongpwd", hashed) is False

def test_email_validator():
    assert is_valid_email("user@example.com")
    assert not is_valid_email("bademail@")

def test_jwt():
    token = create_access_token({"sub": "1"})
    payload = decode_access_token(token)
    assert payload["sub"] == "1"
