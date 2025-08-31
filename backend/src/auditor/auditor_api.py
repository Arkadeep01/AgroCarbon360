## backend/src/auditor/auditor_api.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.dependency import get_db
from . import auditor_service, schemas

router = APIRouter(prefix="/auditor", tags=["auditor"])

@router.post("/report", response_model=schemas.AuditReport)
def create_audit_report(report: schemas.AuditReportCreate, db: Session = Depends(get_db)):
    return auditor_service.create_audit_report(db, report)

@router.get("/report/{report_id}", response_model=list[schemas.AuditReport])
def get_audit_report(report_id: int, entity_type: str, db: Session = Depends(get_db)):
    return auditor_service.get_audit_report(db, report_id, entity_type)

@router.get("/reports/{entity_type}/{entity_id}", response_model=list[schemas.AuditReport])
def list_reports(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    return db.query(auditor_service.models.AuditReport).filter(
        auditor_service.models.AuditReport.entity_type == entity_type,
        auditor_service.models.AuditReport.farmer_id == entity_id if entity_type == "farmer" else
        auditor_service.models.AuditReport.auditor_id == entity_id
    ).all()