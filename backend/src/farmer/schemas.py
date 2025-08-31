## backend/src/farmer/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

class FarmerBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    address: str | None = None
    farm_name: str | None = None
    farm_location: str | None = None
    farm_size: int | None = None  # Size in acres
    crop_type: str | None = None
    irrigation_type: str | None = None
    soil_type: str | None = None
    notes: str | None = None
    status: str | None = "active"  # e.g., active, inactive, suspended
    profile_picture: str | None = None  # URL or path to profile picture
    identification_number: str | None = None  # e.g., government ID

class FarmerCreate(FarmerBase):
    pass

class FarmerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    address: str | None = None
    farm_name: str | None = None
    farm_location: str | None = None
    farm_size: int | None = None  # Size in acres
    crop_type: str | None = None
    irrigation_type: str | None = None
    soil_type: str | None = None
    notes: str | None = None
    status: str | None = None  # e.g., active, inactive, suspended
    profile_picture: str | None = None  # URL or path to profile picture
    identification_number: str | None = None  # e.g., government ID

class FarmerInDBBase(FarmerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Farmer(FarmerInDBBase):
    pass

