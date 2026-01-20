"""DefectType schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DefectTypeBase(BaseModel):
    """Base defect type schema"""
    defect_code: str = Field(..., min_length=1, max_length=50, description="Unique defect code")
    name_vi: str = Field(..., min_length=1, max_length=200, description="Vietnamese name")
    name_en: str = Field(..., min_length=1, max_length=200, description="English name")


class DefectTypeCreate(DefectTypeBase):
    """Schema for creating a defect type"""
    pass


class DefectTypeUpdate(BaseModel):
    """Schema for updating a defect type"""
    defect_code: Optional[str] = Field(None, min_length=1, max_length=50)
    name_vi: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, min_length=1, max_length=200)


class DefectTypeResponse(DefectTypeBase):
    """Schema for defect type response"""
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
            "defect_code": obj.defect_code,
            "name_vi": obj.name_vi,
            "name_en": obj.name_en,
            "display_name": f"{obj.name_vi} ({obj.name_en})",
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        return cls(**data)
