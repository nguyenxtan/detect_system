"""
Base class for all detectors.

All detectors must inherit from BaseDetector to ensure:
- Consistent interface
- Proper error handling
- Audit trail compatibility
- Safe failure modes

CRITICAL: Detectors MUST NOT raise exceptions during detection.
They should return empty results on failure and log the error.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
import logging
from ..types import DefectRegion

# Configure logger
logger = logging.getLogger(__name__)


class BaseDetector(ABC):
    """
    Abstract base class for defect detectors.

    Design requirements:
    - Must be stateless (can process images independently)
    - Must return confidence scores for explainability
    - Must handle edge cases gracefully (NEVER crash the engine)
    - Must validate inputs before processing
    - Must implement both detect() and get_score() methods

    Interface contract:
    1. detect(image) -> List[DefectRegion]  # Returns bounding boxes
    2. get_score(image) -> float            # Returns overall confidence (0.0-1.0)
    """

    def __init__(self, config: dict):
        """
        Initialize detector with configuration.

        Args:
            config: Dictionary of detector-specific parameters

        Raises:
            ValueError: If configuration is invalid during initialization
                       (OK to fail during setup, NOT during detection)
        """
        self.config = config
        self.validate_config()

    @abstractmethod
    def validate_config(self) -> None:
        """
        Validate detector configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    @abstractmethod
    def detect(self, image: np.ndarray) -> List[DefectRegion]:
        """
        Detect defects in the given image.

        CRITICAL: This method MUST NOT raise exceptions.
        On any error, return empty list and log the failure.

        Args:
            image: Input image as numpy array (H, W, C) or (H, W)

        Returns:
            List of detected defect regions (empty if detection fails)

        Failure behavior:
            - Invalid image -> return []
            - Processing error -> return []
            - No defects found -> return []
        """
        pass

    def get_score(self, image: np.ndarray) -> float:
        """
        Get overall detection score for the image.

        This is used for OK/NG decision when no specific regions are found.

        CRITICAL: This method MUST NOT raise exceptions.
        On any error, return 0.0 (assume OK).

        Args:
            image: Input image as numpy array

        Returns:
            Score from 0.0 (normal/OK) to 1.0 (defective/NG)

        Default implementation:
            Returns 1.0 if any defects detected, 0.0 otherwise.
            Subclasses can override for more nuanced scoring.

        Failure behavior:
            - Invalid image -> return 0.0
            - Processing error -> return 0.0
        """
        try:
            regions = self.detect(image)
            return 1.0 if len(regions) > 0 else 0.0
        except Exception as e:
            logger.error(f"{self.get_name()} get_score failed: {e}")
            return 0.0

    def _validate_image(self, image: np.ndarray) -> bool:
        """
        Validate input image format.

        UPDATED: Returns bool instead of raising exceptions.
        This allows detectors to fail gracefully.

        Args:
            image: Input image to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not isinstance(image, np.ndarray):
                logger.warning(f"{self.get_name()}: Image must be a numpy array")
                return False

            if image.size == 0:
                logger.warning(f"{self.get_name()}: Image is empty")
                return False

            if len(image.shape) not in [2, 3]:
                logger.warning(f"{self.get_name()}: Image must be 2D or 3D, got shape {image.shape}")
                return False

            if len(image.shape) == 3 and image.shape[2] not in [1, 3, 4]:
                logger.warning(f"{self.get_name()}: Image channels must be 1, 3, or 4, got {image.shape[2]}")
                return False

            return True

        except Exception as e:
            logger.error(f"{self.get_name()}: Image validation failed with exception: {e}")
            return False

    def get_name(self) -> str:
        """Return detector name for logging and traceability."""
        return self.__class__.__name__

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Common preprocessing steps.

        This method can be overridden by subclasses for detector-specific preprocessing.

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        # Default: return as-is
        # Subclasses can add normalization, resizing, etc.
        return image

    def _create_defect_region(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        confidence: float,
        defect_type: str
    ) -> DefectRegion:
        """
        Helper method to create DefectRegion with detector metadata.

        Args:
            x, y, w, h: Bounding box coordinates
            confidence: Detection confidence (0.0 to 1.0)
            defect_type: Type of defect detected

        Returns:
            DefectRegion instance
        """
        return DefectRegion(
            x=int(x),
            y=int(y),
            w=int(w),
            h=int(h),
            defect_type=defect_type,
            confidence=float(confidence),
            detector_name=self.get_name()
        )
