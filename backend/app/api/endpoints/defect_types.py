"""DefectType management endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.user import User
from app.models.defect_type import DefectType
from app.schemas.defect_type import DefectTypeCreate, DefectTypeUpdate, DefectTypeResponse
from app.core.auth import verify_admin

router = APIRouter()


@router.get("/", response_model=List[DefectTypeResponse])
def get_all_defect_types(
    search: str = Query(None, description="Search by code or name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Get all defect types with optional search (Admin only)
    """
    query = db.query(DefectType)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (DefectType.defect_code.ilike(search_filter)) |
            (DefectType.name_vi.ilike(search_filter)) |
            (DefectType.name_en.ilike(search_filter))
        )

    defect_types = query.offset(skip).limit(limit).all()
    return [DefectTypeResponse.from_orm(dt) for dt in defect_types]


@router.get("/{defect_type_id}", response_model=DefectTypeResponse)
def get_defect_type(
    defect_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Get defect type by ID (Admin only)
    """
    defect_type = db.query(DefectType).filter(DefectType.id == defect_type_id).first()
    if not defect_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Defect type not found"
        )
    return DefectTypeResponse.from_orm(defect_type)


@router.post("/", response_model=DefectTypeResponse, status_code=status.HTTP_201_CREATED)
def create_defect_type(
    defect_type_data: DefectTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Create new defect type (Admin only)
    Enforces unique defect_code
    """
    # Check if defect_code already exists
    existing = db.query(DefectType).filter(
        DefectType.defect_code == defect_type_data.defect_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Defect code '{defect_type_data.defect_code}' already exists"
        )

    # Create new defect type
    new_defect_type = DefectType(
        defect_code=defect_type_data.defect_code,
        name_vi=defect_type_data.name_vi,
        name_en=defect_type_data.name_en
    )

    try:
        db.add(new_defect_type)
        db.commit()
        db.refresh(new_defect_type)
        return DefectTypeResponse.from_orm(new_defect_type)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Defect code must be unique"
        )


@router.put("/{defect_type_id}", response_model=DefectTypeResponse)
def update_defect_type(
    defect_type_id: int,
    defect_type_data: DefectTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Update defect type (Admin only)
    """
    defect_type = db.query(DefectType).filter(DefectType.id == defect_type_id).first()
    if not defect_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Defect type not found"
        )

    # Update defect_code if provided
    if defect_type_data.defect_code is not None:
        if defect_type_data.defect_code != defect_type.defect_code:
            existing = db.query(DefectType).filter(
                DefectType.defect_code == defect_type_data.defect_code,
                DefectType.id != defect_type_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Defect code '{defect_type_data.defect_code}' already exists"
                )
        defect_type.defect_code = defect_type_data.defect_code

    # Update name_vi if provided
    if defect_type_data.name_vi is not None:
        defect_type.name_vi = defect_type_data.name_vi

    # Update name_en if provided
    if defect_type_data.name_en is not None:
        defect_type.name_en = defect_type_data.name_en

    try:
        db.commit()
        db.refresh(defect_type)
        return DefectTypeResponse.from_orm(defect_type)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Defect code must be unique"
        )


@router.delete("/{defect_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_defect_type(
    defect_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Delete defect type (Admin only)
    """
    defect_type = db.query(DefectType).filter(DefectType.id == defect_type_id).first()
    if not defect_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Defect type not found"
        )

    db.delete(defect_type)
    db.commit()
    return None
