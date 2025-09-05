from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Literal
from sqlalchemy.orm import Session
from src.db.dependency import get_db
from . import models

router = APIRouter(prefix="/iot", tags=["iot"])


class DeviceRegister(BaseModel):
    device_id: str
    type: Literal["methane", "soil_carbon"]
    farmer_id: int


class ReadingCreate(BaseModel):
    device_id: str
    timestamp: str
    value: float
    units: str
    latitude: float | None = None
    longitude: float | None = None


@router.post("/devices")
def register_device(body: DeviceRegister, db: Session = Depends(get_db)):
    if db.query(models.Device).filter(models.Device.device_id == body.device_id).first():
        return {"status": "exists", **body.model_dump()}
    rec = models.Device(device_id=body.device_id, type=body.type, farmer_id=body.farmer_id)
    db.add(rec)
    db.commit()
    return {"status": "registered", **body.model_dump()}


@router.post("/readings")
def ingest_reading(body: ReadingCreate, db: Session = Depends(get_db)):
    rec = models.Reading(**body.model_dump())
    db.add(rec)
    db.commit()
    return {"status": "accepted", **body.model_dump()}

