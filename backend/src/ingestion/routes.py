from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class SatelliteTaskCreate(BaseModel):
    source: str  # sentinel2, landsat8, sentinel1
    area_of_interest_geojson: dict
    start_date: str
    end_date: str
    indices: List[str] = ["NDVI"]  # NDVI, EVI, SAR_VV, SAR_VH


@router.post("/satellite/tasks")
def create_satellite_task(task: SatelliteTaskCreate):
    return {"task_id": "sat-001", "status": "queued", "details": task.model_dump()}


@router.get("/satellite/tasks/{task_id}")
def get_satellite_task(task_id: str):
    return {"task_id": task_id, "status": "running"}


@router.post("/uav/upload")
async def upload_uav_images(
    project_id: str = Form(...),
    files: List[UploadFile] = File(...),
):
    filenames = [f.filename for f in files]
    return {"project_id": project_id, "uploaded": filenames}

