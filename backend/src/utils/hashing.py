## backend/src/utils/hashing.py

from passlib.context import CryptContext

# Password hashing context
# Why? bcrypt? It's a widely used and secure hashing algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    return pwd_context.verify(plain_password, hashed_password)