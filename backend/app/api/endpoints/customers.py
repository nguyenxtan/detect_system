"""Customer management endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.core.auth import verify_admin

router = APIRouter()


@router.get("/", response_model=List[CustomerResponse])
def get_all_customers(
    search: str = Query(None, description="Search by code or name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Get all customers with optional search (Admin only)
    """
    query = db.query(Customer)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Customer.customer_code.ilike(search_filter)) |
            (Customer.customer_name.ilike(search_filter))
        )

    customers = query.offset(skip).limit(limit).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Get customer by ID (Admin only)
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Create new customer (Admin only)
    Enforces unique customer_code
    """
    # Check if customer_code already exists
    existing_customer = db.query(Customer).filter(
        Customer.customer_code == customer_data.customer_code
    ).first()

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer code '{customer_data.customer_code}' already exists"
        )

    # Create new customer
    new_customer = Customer(
        customer_code=customer_data.customer_code,
        customer_name=customer_data.customer_name
    )

    try:
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer code must be unique"
        )


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Update customer (Admin only)
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Update customer_code if provided
    if customer_data.customer_code is not None:
        # Check if new code already exists (for different customer)
        if customer_data.customer_code != customer.customer_code:
            existing = db.query(Customer).filter(
                Customer.customer_code == customer_data.customer_code,
                Customer.id != customer_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Customer code '{customer_data.customer_code}' already exists"
                )
        customer.customer_code = customer_data.customer_code

    # Update customer_name if provided
    if customer_data.customer_name is not None:
        customer.customer_name = customer_data.customer_name

    try:
        db.commit()
        db.refresh(customer)
        return customer
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer code must be unique"
        )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Delete customer (Admin only)
    Cannot delete if products exist
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Check if customer has products
    if customer.products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete customer. {len(customer.products)} product(s) are linked to this customer. Please delete or reassign the products first."
        )

    db.delete(customer)
    db.commit()
    return None
