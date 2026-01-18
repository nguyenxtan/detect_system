"""
Vision Pipeline Integration Service

Phase 3: Two-stage defect detection
- Stage 1: VisionEngine detects defects (OK/NG + regions)
- Stage 2: If NG, crop regions and run CLIP matching

This service is the bridge between vision_engine and existing CLIP similarity matching.
"""

import sys
from pathlib import Path
import numpy as np
import cv2
from typing import Optional, Tuple, Dict, Any, List
import logging
import time

# Add vision_engine to path
vision_engine_path = str(Path(__file__).parent.parent.parent.parent / "vision_engine")
if vision_engine_path not in sys.path:
    sys.path.insert(0, vision_engine_path)

from ..core.config import settings
from ..utils.image_utils import crop_defect_region, select_best_region

logger = logging.getLogger(__name__)


class VisionIntegrationService:
    """
    Service for integrating vision pipeline with existing CLIP matching.

    Handles:
    - Vision engine initialization (lazy)
    - Image inspection via VisionEngine
    - Region cropping and selection
    - Fallback to CLIP-only on errors
    """

    def __init__(self):
        self._vision_engine = None
        self._vision_config = None

    def _initialize_vision_engine(self):
        """
        Lazy initialization of vision engine.

        Only initializes if ENABLE_VISION_PIPELINE=True.
        Safe failure: returns False if initialization fails.
        """
        if self._vision_engine is not None:
            return True  # Already initialized

        if not settings.ENABLE_VISION_PIPELINE:
            logger.info("Vision pipeline disabled (ENABLE_VISION_PIPELINE=False)")
            return False

        try:
            # Import vision engine modules
            from vision_engine import VisionEngine, VisionConfig

            # Create configuration
            self._vision_config = VisionConfig(
                anomaly_threshold=settings.VISION_ANOMALY_THRESHOLD,
                enable_crack_detector=True,
                enable_hole_detector=True,
                enable_anomaly_detector=False  # Requires training
            )

            # Initialize engine
            self._vision_engine = VisionEngine(self._vision_config)

            logger.info(f"Vision engine initialized: {self._vision_engine.get_detector_info()}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize vision engine: {e}")
            self._vision_engine = None
            return False

    def inspect_image(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Run vision pipeline on image.

        Args:
            image_data: Raw image bytes

        Returns:
            Inspection result dict with keys:
                - result: "OK" or "NG"
                - anomaly_score: float
                - defect_regions: list of dicts
                - processing_time_ms: float
                - detectors_used: list of str
                - model_version: str
            Or None if vision pipeline is disabled or fails

        Safe failure: Returns None on any error, allowing fallback to CLIP-only
        """
        if not self._initialize_vision_engine():
            return None

        try:
            # Decode image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None or image.size == 0:
                logger.warning("Failed to decode image for vision pipeline")
                return None

            # Run vision inspection
            start_time = time.time()
            result = self._vision_engine.inspect(image, image_id="api_request")
            processing_time = (time.time() - start_time) * 1000

            # Convert to dict
            vision_result = {
                "result": result.result,
                "anomaly_score": result.anomaly_score,
                "defect_regions": [region.to_dict() for region in result.defect_regions],
                "processing_time_ms": processing_time,
                "detectors_used": result.detectors_used or [],
                "model_version": settings.VISION_MODEL_VERSION
            }

            logger.info(f"Vision inspection: {result.result}, {len(result.defect_regions)} regions, {processing_time:.1f}ms")
            return vision_result

        except Exception as e:
            logger.error(f"Vision inspection failed: {e}")
            return None

    def crop_best_region(
        self,
        image_data: bytes,
        defect_regions: List[Dict[str, Any]]
    ) -> Optional[bytes]:
        """
        Crop the best defect region from image.

        Args:
            image_data: Raw image bytes
            defect_regions: List of defect region dicts from vision pipeline

        Returns:
            Cropped image as bytes (JPEG), or None if crop fails

        Strategy: Select largest region by default
        """
        if not defect_regions:
            logger.warning("No defect regions to crop")
            return None

        try:
            # Decode original image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None or image.size == 0:
                logger.warning("Failed to decode image for cropping")
                return None

            # Select best region
            best_region = select_best_region(defect_regions, strategy="largest")
            if not best_region:
                logger.warning("Failed to select best region")
                return None

            # Extract coordinates
            x = best_region.get("x", 0)
            y = best_region.get("y", 0)
            w = best_region.get("w", 0)
            h = best_region.get("h", 0)

            # Crop with padding
            cropped = crop_defect_region(image, x, y, w, h, padding=10)

            if cropped is None or cropped.size == 0:
                logger.warning(f"Failed to crop region ({x},{y},{w},{h})")
                return None

            # Encode back to JPEG bytes
            success, encoded = cv2.imencode('.jpg', cropped)
            if not success:
                logger.warning("Failed to encode cropped image")
                return None

            cropped_bytes = encoded.tobytes()
            logger.info(f"Cropped region ({x},{y},{w},{h}), size: {len(cropped_bytes)} bytes")

            return cropped_bytes

        except Exception as e:
            logger.error(f"Failed to crop best region: {e}")
            return None


# Singleton instance
_vision_service = None


def get_vision_service() -> VisionIntegrationService:
    """
    Get singleton vision integration service.

    Returns:
        VisionIntegrationService instance
    """
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionIntegrationService()
    return _vision_service
