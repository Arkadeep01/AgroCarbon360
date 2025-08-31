## backend/src/verifications/audit_api.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from .. import models, schemas

router = APIRouter(prefix="/audit", tags=["audit"])

@router.post("/log", response_model=schemas.AuditLog)
def create_audit_log(log: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    audit = models.Auditlogs(
        user_id=log.user_id,
        action=log.action,
        timestamp=log.timestamp,
        details=log.details,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return {"msg": "Audit log created", "audit": audit}

@router.get("/{user_id}", response_model=list[schemas.AuditLog])
def get_audit_logs(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(models.Auditlogs).filter(models.Auditlogs.user_id == user_id).all()
    return {"logs": logs}