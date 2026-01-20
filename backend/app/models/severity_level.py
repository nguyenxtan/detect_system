"""SeverityLevel model for database"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class SeverityLevel(Base):
    """SeverityLevel model - catalog of defect severity levels"""
    __tablename__ = "severity_levels"

    id = Column(Integer, primary_key=True, index=True)
    severity_code = Column(String(50), unique=True, nullable=False, index=True)
    name_vi = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
