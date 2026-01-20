"""Defect management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import aiofiles
import logging

logger = logging.getLogger(__name__)
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
# Temporarily disabled Phase 3 vision integration
# from ...services.vision_integration import get_vision_service
import time

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
    customer_id: Optional[int] = Form(None),
    product_id: Optional[int] = Form(None),
    reference_images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new defect profile (Admin/QC only)"""

    # product_id is required for context-based filtering
    if product_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="product_id is required"
        )

    # Validate product and derive customer_id if not provided
    from ...models.product import Product
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with id {product_id} not found"
        )

    # If customer_id provided, validate consistency; otherwise derive from product
    if customer_id is not None:
        if product.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product_id} does not belong to customer {customer_id}"
            )
    else:
        # Derive customer_id from product
        customer_id = product.customer_id

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
        customer_id=customer_id,
        product_id=product_id,
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
    user_id: Optional[str] = Form(None),
    customer_id: Optional[int] = Form(None),
    product_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Match an image to defect profiles (Public endpoint for Telegram bot)

    Context-based filtering (QC-standard):
    - product_id is REQUIRED for context-based matching
    - customer_id is optional (used for validation if provided)
    - Filters candidates by product_id BEFORE similarity matching
    """

    # Get embedding service
    embedding_service = get_embedding_service()

    # Read image
    image_data = await image.read()
    print(f"[DEBUG] Image data size: {len(image_data)} bytes")

    # Generate embedding
    image_embedding = embedding_service.get_image_embedding(image_data)
    print(f"[DEBUG] Generated image_embedding type: {type(image_embedding)}, shape: {image_embedding.shape if hasattr(image_embedding, 'shape') else 'no shape'}")

    # Context-based filtering - product_id is REQUIRED
    query = db.query(DefectProfile)

    if product_id is not None:
        # Validate product exists
        from ...models.product import Product
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with id {product_id} not found"
            )

        # If customer_id provided, validate consistency
        if customer_id is not None and product.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {product_id} does not belong to customer {customer_id}"
            )

        # Filter by product_id BEFORE similarity matching
        print(f"[CONTEXT FILTER] product_id={product_id}, customer_id={customer_id or product.customer_id}")
        query = query.filter(DefectProfile.product_id == product_id)
    else:
        # product_id is required
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="product_id is required for defect matching"
        )

    profiles = query.all()

    if not profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No defect profiles configured for this product"
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

    # Save uploaded image to disk
    uploaded_image_path = None
    if user_id:
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

            # Generate unique filename
            file_extension = os.path.splitext(image.filename or "image.jpg")[1] or ".jpg"
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

            # Save image to disk
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(image_data)

            # Store URL path for database
            uploaded_image_path = f"/uploads/{unique_filename}"
            logger.info(f"Saved uploaded image to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save uploaded image: {e}")
            # Continue even if image save fails

    # Create DefectIncident record if user_id provided
    if user_id and uploaded_image_path:
        try:
            incident = DefectIncident(
                user_id=user_id,
                defect_profile_id=best_match['profile'].id,
                predicted_defect_type=best_match['profile'].defect_type,
                confidence=confidence,
                image_url=uploaded_image_path,
                image_embedding=image_embedding.tolist() if hasattr(image_embedding, 'tolist') else list(image_embedding),
                model_version=settings.MODEL_VERSION if hasattr(settings, 'MODEL_VERSION') else "v1.0",
                notes=text_query or None
            )
            db.add(incident)
            db.commit()
            logger.info(f"Created DefectIncident for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to create DefectIncident: {e}")
            db.rollback()
            # Continue even if incident creation fails

    return DefectMatchResult(
        defect_profile=DefectProfileResponse.model_validate(best_match['profile']),
        confidence=confidence,
        similarity_breakdown={
            "image_weight": settings.IMAGE_WEIGHT,
            "text_weight": settings.TEXT_WEIGHT
        }
    )


@router.post("/inspect")
async def inspect_defect(
    image: UploadFile = File(...),
    text_query: Optional[str] = Form(None),
    match_on_ok: Optional[bool] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Phase 3: Two-stage defect inspection endpoint.

    Stage 1: VisionEngine detects defects (OK/NG + regions)
    Stage 2: If NG (or match_on_ok=True), run CLIP matching

    Args:
        image: Image file to inspect
        text_query: Optional text query for CLIP matching
        match_on_ok: Force CLIP matching even if vision result is OK

    Returns:
        {
            "vision": {
                "result": "OK|NG",
                "anomaly_score": float,
                "defect_regions": [{x,y,w,h,type,confidence}],
                "detectors_used": [str],
                "processing_time_ms": float
            },
            "match": null | {
                "defect_profile": {...},
                "confidence": float
            },
            "processing_time_ms": float
        }

    Behavior:
        - If ENABLE_VISION_PIPELINE=False: Falls back to CLIP-only matching
        - If vision.result="OK": match=null (unless match_on_ok=True)
        - If vision.result="NG": Crops best region and runs CLIP matching
        - On vision failure: Falls back to CLIP-only matching with warning
    """
    start_time = time.time()

    # Read image once
    image_data = await image.read()

    # Get services
    vision_service = None
    if settings.ENABLE_VISION_PIPELINE:
        try:
            from ...services.vision_integration import get_vision_service
            vision_service = get_vision_service()
        except ImportError:
            logger.warning("Vision integration not available, falling back to CLIP-only")

    embedding_service = get_embedding_service()

    # Initialize response
    response = {
        "vision": None,
        "match": None,
        "processing_time_ms": 0.0,
        "fallback_to_clip": False,
        "warning": None
    }

    # STAGE 1: Vision Pipeline
    vision_result = None
    if settings.ENABLE_VISION_PIPELINE and vision_service:
        vision_result = vision_service.inspect_image(image_data)

        if vision_result:
            response["vision"] = vision_result
        else:
            # Vision failed, will fallback to CLIP
            response["fallback_to_clip"] = True
            response["warning"] = "Vision pipeline failed, using CLIP-only matching"
            logger.warning("Vision pipeline failed, falling back to CLIP-only")

    else:
        # Vision pipeline disabled
        response["vision"] = {
            "result": "N/A",
            "message": "Vision pipeline disabled (ENABLE_VISION_PIPELINE=False)"
        }

    # STAGE 2: CLIP Matching Decision
    should_match = False
    image_for_matching = image_data  # Default: use full image

    if vision_result and vision_result["result"] == "NG":
        # Vision detected defects - crop and match
        should_match = True

        # Try to crop best region
        defect_regions = vision_result.get("defect_regions", [])
        if defect_regions and vision_service:
            cropped = vision_service.crop_best_region(image_data, defect_regions)
            if cropped:
                image_for_matching = cropped
                logger.info("Using cropped defect region for CLIP matching")
            else:
                logger.warning("Failed to crop region, using full image for CLIP matching")

    elif match_on_ok or response["fallback_to_clip"]:
        # Either forced matching or fallback mode
        should_match = True

    # Run CLIP matching if needed
    if should_match:
        try:
            # Generate embedding
            image_embedding = embedding_service.get_image_embedding(image_for_matching)

            # Get all profiles
            profiles = db.query(DefectProfile).all()

            if not profiles:
                response["match"] = None
                response["warning"] = "No defect profiles in database"
            else:
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

                if confidence >= settings.SIMILARITY_THRESHOLD:
                    response["match"] = {
                        "defect_profile": DefectProfileResponse.model_validate(best_match['profile']).model_dump(),
                        "confidence": confidence
                    }
                else:
                    response["match"] = None
                    response["warning"] = f"No confident match found (confidence: {confidence:.2f})"

        except Exception as e:
            logger.error(f"CLIP matching failed: {e}")
            response["match"] = None
            response["warning"] = f"CLIP matching error: {str(e)}"

    # Total processing time
    response["processing_time_ms"] = (time.time() - start_time) * 1000

    return response


@router.get("/incidents", response_model=List[DefectIncidentResponse])
def get_defect_incidents(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get defect incidents (requires authentication)"""
    query = db.query(DefectIncident)

    if user_id:
        query = query.filter(DefectIncident.user_id == user_id)

    incidents = query.order_by(DefectIncident.created_at.desc()).offset(skip).limit(limit).all()
    return incidents


@router.get("/incidents/public", response_model=List[DefectIncidentResponse])
def get_defect_incidents_public(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Public endpoint for Telegram bot to retrieve user's incident history.
    Does not require authentication.
    """
    incidents = db.query(DefectIncident).filter(
        DefectIncident.user_id == user_id
    ).order_by(
        DefectIncident.created_at.desc()
    ).limit(limit).all()

    return incidents
