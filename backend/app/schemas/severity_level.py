"""SeverityLevel schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SeverityLevelBase(BaseModel):
    """Base severity level schema"""
    severity_code: str = Field(..., min_length=1, max_length=50, description="Unique severity code")
    name_vi: str = Field(..., min_length=1, max_length=200, description="Vietnamese name")
    name_en: str = Field(..., min_length=1, max_length=200, description="English name")


class SeverityLevelCreate(SeverityLevelBase):
    """Schema for creating a severity level"""
    pass


class SeverityLevelUpdate(BaseModel):
    """Schema for updating a severity level"""
    severity_code: Optional[str] = Field(None, min_length=1, max_length=50)
    name_vi: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, min_length=1, max_length=200)


class SeverityLevelResponse(SeverityLevelBase):
    """Schema for severity level response"""
    id: int
    display_name: str  # Computed field: "name_vi (name_en)"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Override to add computed display_name"""
        data = {
            "id": obj.id,
            "severity_code": obj.severity_code,
            "name_vi": obj.name_vi,
            "name_en": obj.name_en,
            "display_name": f"{obj.name_vi} ({obj.name_en})",
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        return cls(**data)
