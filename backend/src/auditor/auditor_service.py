## backend/src/auditor/auditor_service.py
from sqlalchemy.orm import Session
from . import models, schemas

def create_audit_report(db: Session, report: schemas.AuditReportCreate):
    db_report = models.AuditReport(
        auditor_id=report.auditor_id,
        farmer_id=report.farmer_id,
        findings=report.findings,
        recommendations=report.recommendations,
        status=report.status,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_audit_report(db: Session, report_id: int, entity_type: str):
    return db.query(models.AuditReport).filter(
        models.AuditReport.id == report_id,
        models.AuditReport.entity_type == entity_type
    ).all()

