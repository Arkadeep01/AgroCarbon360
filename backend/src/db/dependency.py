## backend/src/db/dependency.py
from typing import Generator
from sqlalchemy.orm import Session
from .session import SessionLocal

# Generator function to get a database session (Generator[yield_type, send_type, return_type])
def get_db() -> Generator[Session, None, None]:
    """Yields a database session for dependency injection.
       Dependency that provides a database session to routes.
       Yields a SQLAlchemy Session and closes it after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

