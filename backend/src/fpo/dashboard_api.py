## backend/src/fpo/dashboard_api.py
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from backend.src.fpo import schemas, services
from src.db.session import get_db

from src.farmer import models as farmer_models
from src.auth import models as auth_models

router = APIRouter(prefix="/fpo/dashboard", tags=["FPO Dashboard"])

@router.get("/stats")
def get_fpo_dashboard_stats(db: Session = Depends(get_db)):
    """
    Retrieve dashboard statistics for the FPO.
    """
    total_farmers = db.query(farmer_models.Farmer).count()
    active_farmers = db.query(farmer_models.Farmer).filter(farmer_models.Farmer.status == "active").count()
    inactive_farmers = db.query(farmer_models.Farmer).filter(farmer_models.Farmer.status == "inactive").count()
    total_users = db.query(auth_models.User).count()
    
    return {
        "total_farmers": total_farmers,
        "active_farmers": active_farmers,
        "inactive_farmers": inactive_farmers,
        "total_users": total_users,
        "total_revenue": 0,  # Placeholder for future revenue tracking  
    }

@router.get("/farmers", response_model=list[schemas.Farmer])
def get_fpo_farmers(db: Session = Depends(get_db)):
    """
    Retrieve a list of all farmers associated with the FPO.
    """
    farmers = db.query(farmer_models.Farmer).all()
    return farmers

@router.get("/farmer/{farmer_id}")
def get_fpo_farmer_details(farmer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information about a specific farmer by ID.
    """
    farmer = db.query(farmer_models.Farmer).filter(farmer_models.Farmer.id == farmer_id).first()
    if not farmer:
        return {"error": "Farmer not found"}
    return farmer