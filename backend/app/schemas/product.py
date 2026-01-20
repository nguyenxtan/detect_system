"""Product schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema"""
    product_code: str = Field(..., min_length=1, max_length=50, description="Unique product code")
    product_name: str = Field(..., min_length=1, max_length=200, description="Product name")
    customer_id: int = Field(..., description="Customer ID")


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    product_code: Optional[str] = Field(None, min_length=1, max_length=50)
    product_name: Optional[str] = Field(None, min_length=1, max_length=200)
    customer_id: Optional[int] = None


class CustomerInProduct(BaseModel):
    """Nested customer info in product response"""
    id: int
    customer_code: str
    customer_name: str

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """Schema for product response with customer info"""
    id: int
    product_code: str
    product_name: str
    customer_id: int
    customer: CustomerInProduct
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
