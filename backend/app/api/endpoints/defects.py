"""Defect management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import aiofiles
from ...core.database import get_db
from ...api.deps import get_current_user, get_current_admin_user
from ...models.user import User
from ...models.defect import DefectProfile, DefectIncident
from ...schemas.defect import (
    DefectProfileCreate,
    DefectProfileResponse,
    DefectIncidentResponse,
    DefectMatchResult
)
from ...ml import get_embedding_service
from ...core.config import settings

router = APIRouter()


@router.post("/profiles", response_model=DefectProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_defect_profile(
    customer: str = Form(...),
    part_code: str = Form(...),
    part_name: str = Form(...),
    defect_type: str = Form(...),
    defect_title: str = Form(...),
    defect_description: str = Form(...),
    keywords: str = Form(...),  # comma-separated
    severity: str = Form("minor"),
    reference_images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new defect profile (Admin/QC only)"""

    # Get embedding service
    embedding_service = get_embedding_service()

    # Save reference images
    image_urls = []
    image_embeddings = []

    os.makedirs(settings.REFERENCE_DIR, exist_ok=True)

    for image_file in reference_images:
        # Generate unique filename
        file_ext = os.path.splitext(image_file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(settings.REFERENCE_DIR, filename)

        # Save file
        async with aiofiles.open(filepath, 'wb') as f:
            content = await image_file.read()
            await f.write(content)

        # Store URL path instead of filepath for frontend access
        image_urls.append(f"/references/{filename}")

        # Generate embedding
        embedding = embedding_service.get_image_embedding(content)
        image_embeddings.append(embedding)

    # Average image embeddings
    import numpy as np
    avg_image_embedding = np.mean(image_embeddings, axis=0)

    # Generate text embedding
    keywords_list = [k.strip() for k in keywords.split(",")]
    text_for_embedding = f"{defect_title}. {defect_description}. {', '.join(keywords_list)}"
    text_embedding = embedding_service.get_text_embedding(text_for_embedding)

    # Create defect profile
    profile = DefectProfile(
        customer=customer,
        part_code=part_code,
        part_name=part_name,
        defect_type=defect_type,
        defect_title=defect_title,
        defect_description=defect_description,
        keywords=keywords_list,
        severity=severity,
        reference_images=image_urls,
        image_embedding=avg_image_embedding.tolist(),
        text_embedding=text_embedding.tolist()
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.get("/profiles", response_model=List[DefectProfileResponse])
def get_defect_profiles(
    skip: int = 0,
    limit: int = 100,
    defect_type: Optional[str] = None,
    customer: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all defect profiles"""
    query = db.query(DefectProfile)

    if defect_type:
        query = query.filter(DefectProfile.defect_type == defect_type)

    if customer:
        query = query.filter(DefectProfile.customer == customer)

    profiles = query.offset(skip).limit(limit).all()
    return profiles


@router.get("/profiles/{profile_id}", response_model=DefectProfileResponse)
def get_defect_profile(
    profile_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific defect profile"""
    profile = db.query(DefectProfile).filter(DefectProfile.id == profile_id).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Defect profile not found"
        )

    return profile


@router.post("/match", response_model=DefectMatchResult)
async def match_defect(
    image: UploadFile = File(...),
    text_query: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Match an image to defect profiles (Public endpoint for Telegram bot)"""

    # Get embedding service
    embedding_service = get_embedding_service()

    # Read image
    image_data = await image.read()
    print(f"[DEBUG] Image data size: {len(image_data)} bytes")

    # Generate embedding
    image_embedding = embedding_service.get_image_embedding(image_data)
    print(f"[DEBUG] Generated image_embedding type: {type(image_embedding)}, shape: {image_embedding.shape if hasattr(image_embedding, 'shape') else 'no shape'}")

    # Get all profiles
    profiles = db.query(DefectProfile).all()

    if not profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No defect profiles found in database"
        )

    # Convert to dict for matching
    profile_dicts = []
    for p in profiles:
        profile_dicts.append({
            'id': p.id,
            'image_embedding': p.image_embedding,
            'text_embedding': p.text_embedding,
            'profile': p
        })

    # Find best match
    best_match, confidence = embedding_service.find_best_match(
        image_embedding,
        text_query or "",
        profile_dicts
    )

    if confidence < settings.SIMILARITY_THRESHOLD:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No confident match found (confidence: {confidence:.2f})"
        )

    return DefectMatchResult(
        defect_profile=DefectProfileResponse.model_validate(best_match['profile']),
        confidence=confidence,
        similarity_breakdown={
            "image_weight": settings.IMAGE_WEIGHT,
            "text_weight": settings.TEXT_WEIGHT
        }
    )


@router.get("/incidents", response_model=List[DefectIncidentResponse])
def get_defect_incidents(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get defect incidents"""
    query = db.query(DefectIncident)

    if user_id:
        query = query.filter(DefectIncident.user_id == user_id)

    incidents = query.order_by(DefectIncident.created_at.desc()).offset(skip).limit(limit).all()
    return incidents
