## backend/src/db/init_db.py
from .base_class import Base
from .session import engine
from ..auth.models import User  # Import models so Base knows about them

def init_db():
    Base.metadata.create_all(bind=engine)
