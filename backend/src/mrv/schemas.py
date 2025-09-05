from pydantic import BaseModel
from datetime import datetime


class MRVReportCreate(BaseModel):
    project_id: str
    methodology: str
    location: str
    vintage_year: int
    verified_tonnes: float
    verification_id: str


class MRVReportOut(MRVReportCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


