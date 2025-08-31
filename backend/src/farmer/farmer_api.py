## backend/src/farmer/farmer_api.py
from sqlalchemy.orm import Session
from src.farmer import schemas, services

class FarmerAPI:
    def __init__(self, db: Session):
        self.db = db

    def create_farmer(self, farmer_in: schemas.FarmerCreate) -> schemas.FarmerOut:
        return services.create_farmer(self.db, farmer_in)

    def get_farmer(self, farmer_id: int) -> schemas.FarmerOut:
        return services.get_farmer(self.db, farmer_id)

    def list_farmers(self, skip: int = 0, limit: int = 10) -> list[schemas.FarmerOut]:
        return services.list_farmers(self.db, skip=skip, limit=limit)