from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from typing import Optional
from src.db.dependency import get_db
from . import models, schemas

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/photo", response_model=schemas.PhotoUploadOut)
async def upload_photo(
    farmer_id: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    timestamp: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    stored_path = f"data/photos/{farmer_id}/{file.filename}"
    record = models.PhotoUpload(
        farmer_id=farmer_id,
        filename=file.filename,
        stored_path=stored_path,
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/voice", response_model=schemas.VoiceUploadOut)
async def upload_voice(
    farmer_id: int = Form(...),
    language: str = Form("en"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    stored_path = f"data/voice/{farmer_id}/{file.filename}"
    record = models.VoiceUpload(
        farmer_id=farmer_id,
        filename=file.filename,
        stored_path=stored_path,
        language=language,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

