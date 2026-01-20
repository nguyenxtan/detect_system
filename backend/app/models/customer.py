"""Customer model for database"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Customer(Base):
    """Customer model - represents a client/company"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to products
    products = relationship("Product", back_populates="customer", cascade="all, delete-orphan")
