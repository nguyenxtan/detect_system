"""Defect schemas"""
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import uuid
import os


class DefectProfileCreate(BaseModel):
    """Schema for creating defect profile"""
    customer: str
    part_code: str
    part_name: str
    defect_type: str
    defect_title: str
    defect_description: str
    keywords: List[str]
    severity: str = "minor"
    # Context filtering fields
    customer_id: Optional[int] = None
    product_id: Optional[int] = None


class DefectProfileResponse(BaseModel):
    """Schema for defect profile response"""
    id: uuid.UUID
    customer: str
    part_code: str
    part_name: str
    defect_type: str
    defect_title: str
    defect_description: str
    keywords: List[str]
    severity: str
    reference_images: Optional[List[str]] = []
    created_at: datetime
    # Context filtering fields
    customer_id: Optional[int] = None
    product_id: Optional[int] = None

    @field_validator('reference_images', mode='after')
    @classmethod
    def convert_old_paths(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Convert old file paths to new URL paths for backward compatibility"""
        if not v:
            return v

        converted = []
        for path in v:
            # If path starts with ./data/reference_images/, convert to /references/
            if path.startswith('./data/reference_images/') or path.startswith('data/reference_images/'):
                filename = os.path.basename(path)
                converted.append(f'/references/{filename}')
            # If path already starts with /references/, keep it as is
            elif path.startswith('/references/'):
                converted.append(path)
            else:
                # Fallback: try to extract filename and create path
                filename = os.path.basename(path)
                converted.append(f'/references/{filename}')

        return converted

    class Config:
        from_attributes = True


class DefectIncidentCreate(BaseModel):
    """Schema for creating defect incident"""
    user_id: str
    image_url: str
    notes: Optional[str] = None


class DefectIncidentResponse(BaseModel):
    """Schema for defect incident response"""
    id: uuid.UUID
    user_id: str
    defect_profile_id: Optional[uuid.UUID]
    predicted_defect_type: Optional[str]
    confidence: Optional[float]
    image_url: str
    model_version: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DefectMatchResult(BaseModel):
    """Schema for defect matching result"""
    defect_profile: Optional[DefectProfileResponse]
    confidence: float
    similarity_breakdown: Optional[dict] = None
    warning: Optional[str] = None
