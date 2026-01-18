"""
Crack Detector using rule-based OpenCV methods.

Crack characteristics in PE/PU materials:
- Thin, elongated dark regions
- High aspect ratio (length >> width)
- Roughly linear or slightly curved

Method:
1. Edge detection (Canny)
2. Morphological operations to connect nearby edges
3. Contour analysis to find thin, elongated shapes
4. Filter by aspect ratio and length

NOT suitable for:
- Micro-cracks (< 5 pixels wide)
- Extremely curved or branching cracks
- Cracks with low contrast

QC Note:
This detector is conservative. Adjust thresholds based on
actual defect samples from production line.
"""

from typing import List
import numpy as np
import cv2
from .base import BaseDetector
from ..types import DefectRegion


class CrackDetector(BaseDetector):
    """
    Rule-based crack detector using OpenCV.

    Parameters:
        min_length: Minimum crack length in pixels (default: 20)
        max_width: Maximum crack width in pixels (default: 5)
        confidence_threshold: Minimum confidence to report (default: 0.7)
        edge_threshold_low: Canny low threshold (default: 50)
        edge_threshold_high: Canny high threshold (default: 150)
        min_aspect_ratio: Minimum length/width ratio (default: 3.0)
    """

    def validate_config(self) -> None:
        """Validate crack detector configuration."""
        required = ['min_length', 'max_width', 'confidence_threshold']
        for key in required:
            if key not in self.config:
                raise ValueError(f"Missing required config: {key}")

        if self.config['min_length'] <= 0:
            raise ValueError("min_length must be positive")

        if self.config['max_width'] <= 0:
            raise ValueError("max_width must be positive")

    def detect(self, image: np.ndarray) -> List[DefectRegion]:
        """
        Detect crack-like defects in the image.

        SAFE FAILURE: Never raises exceptions. Returns empty list on any error.

        Args:
            image: Input image (grayscale or color)

        Returns:
            List of detected crack regions (empty list if error or no cracks)
        """
        try:
            # Validate image
            if not self._validate_image(image):
                return []

            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()

            # Detect cracks
            regions = self._detect_cracks(gray)

            return regions

        except Exception as e:
            # Log error but do not crash
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"CrackDetector.detect failed: {e}")
            return []

    def _detect_cracks(self, gray: np.ndarray) -> List[DefectRegion]:
        """
        Internal crack detection logic.

        Args:
            gray: Grayscale image

        Returns:
            List of detected crack regions
        """
        # Step 1: Edge detection
        edge_low = self.config.get('edge_threshold_low', 50)
        edge_high = self.config.get('edge_threshold_high', 150)
        edges = cv2.Canny(gray, edge_low, edge_high)

        # Step 2: Morphological closing to connect nearby edges
        # This helps connect broken crack segments
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # Step 3: Find contours
        contours, _ = cv2.findContours(
            edges_closed,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Step 4: Filter contours by crack criteria
        regions = []
        for contour in contours:
            region = self._analyze_contour(contour)
            if region is not None:
                regions.append(region)

        return regions

    def _analyze_contour(self, contour: np.ndarray) -> DefectRegion:
        """
        Analyze a contour to determine if it represents a crack.

        Args:
            contour: OpenCV contour

        Returns:
            DefectRegion if contour matches crack criteria, None otherwise
        """
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)

        # Calculate dimensions
        length = max(w, h)
        width = min(w, h)

        # Filter 1: Check minimum length
        min_length = self.config['min_length']
        if length < min_length:
            return None

        # Filter 2: Check maximum width
        max_width = self.config['max_width']
        if width > max_width:
            return None

        # Filter 3: Check aspect ratio (must be elongated)
        min_aspect_ratio = self.config.get('min_aspect_ratio', 3.0)
        if width == 0:
            aspect_ratio = float('inf')
        else:
            aspect_ratio = length / width

        if aspect_ratio < min_aspect_ratio:
            return None

        # Calculate confidence based on how well it matches crack criteria
        confidence = self._calculate_confidence(contour, length, width, aspect_ratio)

        # Filter 4: Check confidence threshold
        confidence_threshold = self.config['confidence_threshold']
        if confidence < confidence_threshold:
            return None

        # Create defect region
        return self._create_defect_region(
            x=x,
            y=y,
            w=w,
            h=h,
            confidence=confidence,
            defect_type="crack"
        )

    def _calculate_confidence(
        self,
        contour: np.ndarray,
        length: float,
        width: float,
        aspect_ratio: float
    ) -> float:
        """
        Calculate detection confidence based on crack characteristics.

        Confidence factors:
        - Higher aspect ratio = more crack-like
        - Straighter contour = more crack-like
        - Appropriate size = more crack-like

        Args:
            contour: OpenCV contour
            length: Crack length
            width: Crack width
            aspect_ratio: Length/width ratio

        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence from aspect ratio
        # Map aspect_ratio to confidence: 3.0 -> 0.6, 10.0+ -> 1.0
        aspect_confidence = min(1.0, (aspect_ratio - 3.0) / 7.0 + 0.6)

        # Straightness: compare contour perimeter to bounding rect diagonal
        perimeter = cv2.arcLength(contour, closed=True)
        diagonal = np.sqrt(length**2 + width**2)
        if diagonal > 0:
            straightness = min(1.0, diagonal / perimeter)
        else:
            straightness = 0.0

        # Combine factors (can be tuned based on real data)
        confidence = 0.7 * aspect_confidence + 0.3 * straightness

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
