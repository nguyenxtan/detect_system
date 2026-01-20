"""Customer schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    """Base customer schema"""
    customer_code: str = Field(..., min_length=1, max_length=50, description="Unique customer code")
    customer_name: str = Field(..., min_length=1, max_length=200, description="Customer name")


class CustomerCreate(CustomerBase):
    """Schema for creating a customer"""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating a customer"""
    customer_code: Optional[str] = Field(None, min_length=1, max_length=50)
    customer_name: Optional[str] = Field(None, min_length=1, max_length=200)


class CustomerResponse(CustomerBase):
    """Schema for customer response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
