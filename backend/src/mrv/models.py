from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from ..db.base_class import Base


class MRVReport(Base):
    __tablename__ = "mrv_reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, index=True, nullable=False)
    methodology = Column(String, nullable=False)
    location = Column(String, nullable=False)
    vintage_year = Column(Integer, nullable=False)
    verified_tonnes = Column(Float, nullable=False)
    verification_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


