## backend/src/farmer/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from . import schemas, service
from .forms import FarmerForm

router = APIRouter(prefix="/farmers", tags=["farmers"])

@router.post("/", response_model=schemas.Farmer)
def create_farmer(farmer: schemas.FarmerCreate, db: Session = Depends(get_db)):
    return service.create_farmer(db, farmer)

@router.get("/{farmer_id}", response_model=schemas.Farmer)
def read_farmer(farmer_id: int, db: Session = Depends(get_db)):
    db_farmer = service.get_farmer(db, farmer_id)
    if db_farmer is None:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return db_farmer

@router.get("/", response_model=list[schemas.Farmer])
def list_farmers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_farmers(db, skip=skip, limit=limit)

@router.put("/{farmer_id}", response_model=schemas.Farmer)
def update_farmer(farmer_id: int, farmer_update: schemas.FarmerUpdate, db: Session = Depends(get_db)):
    db_farmer = service.update_farmer(db, farmer_id, farmer_update)
    if db_farmer is None:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return db_farmer

@router.delete("/{farmer_id}", response_model=schemas.Farmer)
def delete_farmer(farmer_id: int, db: Session = Depends(get_db)):
    db_farmer = service.delete_farmer(db, farmer_id)
    if db_farmer is None:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return {"details": "Farmer deleted successfully"}

@router.post("/form", response_model=schemas.Farmer)
def create_farmer_from_form(
    farmer_form: FarmerForm = Depends(FarmerForm.as_form), 
    db: Session = Depends(get_db),
):
    farmer_data = schemas.FarmerCreate(
        name=farmer_form.name,
        email=farmer_form.email,
        phone_number=farmer_form.phone_number,
        address=farmer_form.address,
        farm_name=farmer_form.farm_name,
        farm_location=farmer_form.farm_location,
        farm_size=farmer_form.farm_size,
        crop_type=farmer_form.crop_type,
        irrigation_type=farmer_form.irrigation_type,
        soil_type=farmer_form.soil_type,
        notes=farmer_form.notes,
        status=farmer_form.status,
        profile_picture=farmer_form.profile_picture,
        identification_number=farmer_form.identification_number,
    )
    return service.create_farmer(db, farmer_data)