from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from ..db.base_class import Base


class Device(Base):
    __tablename__ = "iot_devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)
    farmer_id = Column(Integer, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Reading(Base):
    __tablename__ = "iot_readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    timestamp = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    units = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


