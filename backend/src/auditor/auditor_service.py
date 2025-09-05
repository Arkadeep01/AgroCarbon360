## backend/src/auditor/auditor_service.py
from sqlalchemy.orm import Session
from . import models, schemas


def create_audit_log(db: Session, log: schemas.AuditLogCreate):
    db_log = models.Auditlogs(
        auditor_id=log.auditor_id,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        action=log.action,
        timestamp=log.timestamp,
        details=log.details,
        status=log.status,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_audit_log(db: Session, log_id: int):
    return db.query(models.Auditlogs).filter(models.Auditlogs.id == log_id).first()


def list_audit_logs(db: Session, entity_type: str, entity_id: int):
    return db.query(models.Auditlogs).filter(
        models.Auditlogs.entity_type == entity_type,
        models.Auditlogs.entity_id == entity_id,
    ).all()

