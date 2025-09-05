from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from ..db.base_class import Base


class PhotoUpload(Base):
    __tablename__ = "photo_uploads"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, index=True, nullable=False)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class VoiceUpload(Base):
    __tablename__ = "voice_uploads"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, index=True, nullable=False)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)


