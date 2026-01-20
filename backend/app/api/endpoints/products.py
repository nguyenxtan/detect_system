"""Product management endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.auth import verify_admin

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
def get_all_products(
    search: str = Query(None, description="Search by product code or name"),
    customer_id: int = Query(None, description="Filter by customer ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Get all products with optional search and filter (Admin only)
    """
    query = db.query(Product)

    # Filter by customer
    if customer_id:
        query = query.filter(Product.customer_id == customer_id)

    # Search by product code or name
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Product.product_code.ilike(search_filter)) |
            (Product.product_name.ilike(search_filter))
        )

    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Get product by ID (Admin only)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Create new product (Admin only)
    Enforces unique product_code and valid customer_id
    """
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == product_data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {product_data.customer_id} not found"
        )

    # Check if product_code already exists
    existing_product = db.query(Product).filter(
        Product.product_code == product_data.product_code
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product code '{product_data.product_code}' already exists"
        )

    # Create new product
    new_product = Product(
        product_code=product_data.product_code,
        product_name=product_data.product_name,
        customer_id=product_data.customer_id
    )

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code must be unique or customer does not exist"
        )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Update product (Admin only)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Update product_code if provided
    if product_data.product_code is not None:
        if product_data.product_code != product.product_code:
            # Check if new code already exists
            existing = db.query(Product).filter(
                Product.product_code == product_data.product_code,
                Product.id != product_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product code '{product_data.product_code}' already exists"
                )
        product.product_code = product_data.product_code

    # Update product_name if provided
    if product_data.product_name is not None:
        product.product_name = product_data.product_name

    # Update customer_id if provided
    if product_data.customer_id is not None:
        # Check if customer exists
        customer = db.query(Customer).filter(Customer.id == product_data.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {product_data.customer_id} not found"
            )
        product.customer_id = product_data.customer_id

    try:
        db.commit()
        db.refresh(product)
        return product
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code must be unique or customer does not exist"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Delete product (Admin only)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()
    return None
