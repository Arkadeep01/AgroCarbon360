## backend/src/auditor/auditor_api.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from . import auditor_service, schemas
from src.auth.permissions import require_role

router = APIRouter(prefix="/auditor", tags=["auditor"])

@router.post("/log", response_model=schemas.AuditLog)
def create_audit_log(log: schemas.AuditLogCreate, db: Session = Depends(get_db), current_user = Depends(require_role("auditor"))):
    return auditor_service.create_audit_log(db, log)

@router.get("/log/{log_id}", response_model=schemas.AuditLog)
def get_audit_log(log_id: int, db: Session = Depends(get_db)):
    return auditor_service.get_audit_log(db, log_id)

@router.get("/logs/{entity_type}/{entity_id}", response_model=list[schemas.AuditLog])
def list_logs(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    return auditor_service.list_audit_logs(db, entity_type, entity_id)