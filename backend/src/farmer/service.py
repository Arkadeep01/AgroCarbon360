from sqlalchemy.orm import Session
from . import models, schemas


def create_farmer(db: Session, farmer_in: schemas.FarmerCreate) -> models.Farmer:
    db_farmer = models.Farmer(
        name=farmer_in.name,
        email=farmer_in.email,
        phone_number=farmer_in.phone_number,
        address=farmer_in.address,
        farm_name=farmer_in.farm_name,
        farm_location=farmer_in.farm_location,
        farm_size=farmer_in.farm_size,
        crop_type=farmer_in.crop_type,
        irrigation_type=farmer_in.irrigation_type,
        soil_type=farmer_in.soil_type,
        notes=farmer_in.notes,
        status=farmer_in.status,
        profile_picture=farmer_in.profile_picture,
        identification_number=farmer_in.identification_number,
    )
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


def get_farmer(db: Session, farmer_id: int) -> models.Farmer | None:
    return db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()


def get_farmers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Farmer).offset(skip).limit(limit).all()


def update_farmer(db: Session, farmer_id: int, farmer_update: schemas.FarmerUpdate) -> models.Farmer | None:
    db_farmer = get_farmer(db, farmer_id)
    if not db_farmer:
        return None
    update_data = farmer_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_farmer, key, value)
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer


def delete_farmer(db: Session, farmer_id: int) -> models.Farmer | None:
    db_farmer = get_farmer(db, farmer_id)
    if not db_farmer:
        return None
    db.delete(db_farmer)
    db.commit()
    return db_farmer
