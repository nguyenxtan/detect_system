"""Defect models"""
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
from ..core.database import Base


class DefectProfile(Base):
    """Defect Profile - Knowledge Base"""
    __tablename__ = "defect_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer = Column(String(100), nullable=False, index=True)  # e.g., "FAPV"
    part_code = Column(String(50), nullable=False, index=True)  # e.g., "GD3346"
    part_name = Column(String(100), nullable=False)  # e.g., "Grommet"
    defect_type = Column(String(50), nullable=False, index=True)  # can, rach, nhan, phong, ok
    defect_title = Column(String(200), nullable=False)  # e.g., "Cấn"
    defect_description = Column(Text, nullable=False)  # Full QC description
    keywords = Column(ARRAY(String))  # ["can", "vet lom", "ep", "gap"]
    severity = Column(String(20), default="minor")  # minor, major, critical
    reference_images = Column(ARRAY(String))  # List of image URLs
    image_embedding = Column(Vector(512))  # CLIP image embedding
    text_embedding = Column(Vector(512))  # CLIP text embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DefectIncident(Base):
    """Defect Incident - User submissions via Telegram"""
    __tablename__ = "defect_incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False, index=True)  # Telegram user ID
    defect_profile_id = Column(UUID(as_uuid=True), ForeignKey("defect_profiles.id"))
    predicted_defect_type = Column(String(50))
    confidence = Column(Float)  # Similarity score
    image_url = Column(String(500), nullable=False)
    image_embedding = Column(Vector(512))  # User image embedding
    model_version = Column(String(50))  # Track model version
    notes = Column(Text)  # Optional user notes
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
