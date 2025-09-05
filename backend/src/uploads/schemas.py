from pydantic import BaseModel
from datetime import datetime


class PhotoUploadOut(BaseModel):
    id: int
    farmer_id: int
    filename: str
    stored_path: str
    latitude: float
    longitude: float
    timestamp: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True


class VoiceUploadOut(BaseModel):
    id: int
    farmer_id: int
    filename: str
    stored_path: str
    language: str
    created_at: datetime

    class Config:
        orm_mode = True


