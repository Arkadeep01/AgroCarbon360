## backend/src/auditor/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base_class import Base
from datetime import datetime

class Auditlogs(Base):
    __tablename__ = "auditlogs"
    
    id = Column(Integer, primary_key=True, index=True)
    auditor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity_type = Column(String(50), nullable=False)  
    entity_id = Column(Integer, nullable=False)
    action = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    
    auditor = relationship("User", back_populates="audit_logs")