## backend/src/farmer/models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..db.base_class import Base

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    address = Column(String, nullable=True)
    farm_name = Column(String, nullable=True)
    farm_location = Column(String, nullable=True)
    farm_size = Column(Integer, nullable=True)  # Size in acres
    crop_type = Column(String, nullable=True)
    irrigation_type = Column(String, nullable=True)
    soil_type = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    status = Column(String, default="active")  # e.g., active, inactive, suspended
    profile_picture = Column(String, nullable=True)  # URL or path to profile picture
    identification_number = Column(String, unique=True, nullable=True)  # e.g., government