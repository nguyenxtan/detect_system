"""SeverityLevel management endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.user import User
from app.models.severity_level import SeverityLevel
from app.schemas.severity_level import SeverityLevelCreate, SeverityLevelUpdate, SeverityLevelResponse
from app.core.auth import verify_admin

router = APIRouter()


@router.get("/", response_model=List[SeverityLevelResponse])
def get_all_severity_levels(
    search: str = Query(None, description="Search by code or name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Get all severity levels with optional search (Admin only)
    """
    query = db.query(SeverityLevel)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (SeverityLevel.severity_code.ilike(search_filter)) |
            (SeverityLevel.name_vi.ilike(search_filter)) |
            (SeverityLevel.name_en.ilike(search_filter))
        )

    severity_levels = query.offset(skip).limit(limit).all()
    return [SeverityLevelResponse.from_orm(sl) for sl in severity_levels]


@router.get("/{severity_level_id}", response_model=SeverityLevelResponse)
def get_severity_level(
    severity_level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Get severity level by ID (Admin only)
    """
    severity_level = db.query(SeverityLevel).filter(SeverityLevel.id == severity_level_id).first()
    if not severity_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Severity level not found"
        )
    return SeverityLevelResponse.from_orm(severity_level)


@router.post("/", response_model=SeverityLevelResponse, status_code=status.HTTP_201_CREATED)
def create_severity_level(
    severity_level_data: SeverityLevelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Create new severity level (Admin only)
    Enforces unique severity_code
    """
    # Check if severity_code already exists
    existing = db.query(SeverityLevel).filter(
        SeverityLevel.severity_code == severity_level_data.severity_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Severity code '{severity_level_data.severity_code}' already exists"
        )

    # Create new severity level
    new_severity_level = SeverityLevel(
        severity_code=severity_level_data.severity_code,
        name_vi=severity_level_data.name_vi,
        name_en=severity_level_data.name_en
    )

    try:
        db.add(new_severity_level)
        db.commit()
        db.refresh(new_severity_level)
        return SeverityLevelResponse.from_orm(new_severity_level)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Severity code must be unique"
        )


@router.put("/{severity_level_id}", response_model=SeverityLevelResponse)
def update_severity_level(
    severity_level_id: int,
    severity_level_data: SeverityLevelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Update severity level (Admin only)
    """
    severity_level = db.query(SeverityLevel).filter(SeverityLevel.id == severity_level_id).first()
    if not severity_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Severity level not found"
        )

    # Update severity_code if provided
    if severity_level_data.severity_code is not None:
        if severity_level_data.severity_code != severity_level.severity_code:
            existing = db.query(SeverityLevel).filter(
                SeverityLevel.severity_code == severity_level_data.severity_code,
                SeverityLevel.id != severity_level_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Severity code '{severity_level_data.severity_code}' already exists"
                )
        severity_level.severity_code = severity_level_data.severity_code

    # Update name_vi if provided
    if severity_level_data.name_vi is not None:
        severity_level.name_vi = severity_level_data.name_vi

    # Update name_en if provided
    if severity_level_data.name_en is not None:
        severity_level.name_en = severity_level_data.name_en

    try:
        db.commit()
        db.refresh(severity_level)
        return SeverityLevelResponse.from_orm(severity_level)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Severity code must be unique"
        )


@router.delete("/{severity_level_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_severity_level(
    severity_level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin)
):
    """
    Delete severity level (Admin only)
    """
    severity_level = db.query(SeverityLevel).filter(SeverityLevel.id == severity_level_id).first()
    if not severity_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Severity level not found"
        )

    db.delete(severity_level)
    db.commit()
    return None
