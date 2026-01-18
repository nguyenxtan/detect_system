"""
Hole/Void Detector using rule-based OpenCV methods.

Hole characteristics in PE/PU materials:
- Dark circular or elliptical regions
- Relatively uniform intensity
- Defined boundaries
- Size range depends on material and process

Method:
1. Threshold to find dark regions
2. Contour detection
3. Filter by area and circularity
4. Validate intensity uniformity

NOT suitable for:
- Very small holes (< 20 pixels area)
- Holes with irregular boundaries
- Holes in highly textured surfaces

QC Note:
Adjust area thresholds based on acceptable vs. critical hole sizes
as defined in quality standards.
"""

from typing import List
import numpy as np
import cv2
from .base import BaseDetector
from ..types import DefectRegion


class HoleDetector(BaseDetector):
    """
    Rule-based hole/void detector using OpenCV.

    Parameters:
        min_area: Minimum hole area in pixels (default: 50)
        max_area: Maximum hole area in pixels (default: 5000)
        circularity_threshold: Minimum circularity (0-1, default: 0.6)
        intensity_threshold: Maximum intensity for dark regions (default: 80)
        confidence_threshold: Minimum confidence to report (default: 0.7)
    """

    def validate_config(self) -> None:
        """Validate hole detector configuration."""
        required = ['min_area', 'max_area', 'circularity_threshold']
        for key in required:
            if key not in self.config:
                raise ValueError(f"Missing required config: {key}")

        if self.config['min_area'] <= 0:
            raise ValueError("min_area must be positive")

        if self.config['max_area'] < self.config['min_area']:
            raise ValueError("max_area must be >= min_area")

    def detect(self, image: np.ndarray) -> List[DefectRegion]:
        """
        Detect hole/void defects in the image.

        SAFE FAILURE: Never raises exceptions. Returns empty list on any error.

        Args:
            image: Input image (grayscale or color)

        Returns:
            List of detected hole regions (empty list if error or no holes)
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

            # Detect holes
            regions = self._detect_holes(gray)

            return regions

        except Exception as e:
            # Log error but do not crash
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"HoleDetector.detect failed: {e}")
            return []

    def _detect_holes(self, gray: np.ndarray) -> List[DefectRegion]:
        """
        Internal hole detection logic.

        Args:
            gray: Grayscale image

        Returns:
            List of detected hole regions
        """
        # Step 1: Threshold to find dark regions
        # Holes are typically darker than surrounding material
        intensity_threshold = self.config.get('intensity_threshold', 80)
        _, binary = cv2.threshold(
            gray,
            intensity_threshold,
            255,
            cv2.THRESH_BINARY_INV  # Invert so holes are white
        )

        # Step 2: Optional noise reduction
        # Remove small noise that might be mistaken for tiny holes
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Step 3: Find contours
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Step 4: Filter contours by hole criteria
        regions = []
        for contour in contours:
            region = self._analyze_contour(contour, gray)
            if region is not None:
                regions.append(region)

        return regions

    def _analyze_contour(self, contour: np.ndarray, gray: np.ndarray) -> DefectRegion:
        """
        Analyze a contour to determine if it represents a hole.

        Args:
            contour: OpenCV contour
            gray: Original grayscale image (for intensity validation)

        Returns:
            DefectRegion if contour matches hole criteria, None otherwise
        """
        # Calculate contour properties
        area = cv2.contourArea(contour)

        # Filter 1: Check area range
        min_area = self.config['min_area']
        max_area = self.config['max_area']
        if area < min_area or area > max_area:
            return None

        # Filter 2: Check circularity
        perimeter = cv2.arcLength(contour, closed=True)
        if perimeter == 0:
            return None

        # Circularity formula: 4π * area / perimeter²
        # Perfect circle = 1.0, lower values = less circular
        circularity = (4 * np.pi * area) / (perimeter * perimeter)

        circularity_threshold = self.config['circularity_threshold']
        if circularity < circularity_threshold:
            return None

        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)

        # Filter 3: Validate intensity uniformity
        # Holes should have relatively uniform dark intensity
        if not self._validate_intensity_uniformity(contour, gray):
            return None

        # Calculate confidence
        confidence = self._calculate_confidence(area, circularity)

        # Filter 4: Check confidence threshold
        confidence_threshold = self.config.get('confidence_threshold', 0.7)
        if confidence < confidence_threshold:
            return None

        # Create defect region
        return self._create_defect_region(
            x=x,
            y=y,
            w=w,
            h=h,
            confidence=confidence,
            defect_type="hole"
        )

    def _validate_intensity_uniformity(
        self,
        contour: np.ndarray,
        gray: np.ndarray
    ) -> bool:
        """
        Check if the region has uniform intensity (characteristic of holes).

        Args:
            contour: OpenCV contour
            gray: Grayscale image

        Returns:
            True if intensity is sufficiently uniform
        """
        # Create mask for this contour
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)

        # Extract pixel values within contour
        pixels = gray[mask == 255]

        if len(pixels) == 0:
            return False

        # Calculate intensity statistics
        mean_intensity = np.mean(pixels)
        std_intensity = np.std(pixels)

        # Holes should have:
        # 1. Low mean intensity (dark)
        # 2. Low standard deviation (uniform)
        max_mean = self.config.get('intensity_threshold', 80)
        max_std = self.config.get('max_intensity_std', 20)

        if mean_intensity > max_mean:
            return False

        if std_intensity > max_std:
            return False

        return True

    def _calculate_confidence(self, area: float, circularity: float) -> float:
        """
        Calculate detection confidence based on hole characteristics.

        Confidence factors:
        - Higher circularity = more hole-like
        - Appropriate size = more hole-like

        Args:
            area: Hole area in pixels
            circularity: Circularity metric (0-1)

        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Circularity confidence (0.6 -> 0.6, 1.0 -> 1.0)
        circularity_min = self.config['circularity_threshold']
        circularity_range = 1.0 - circularity_min
        if circularity_range > 0:
            circularity_conf = (circularity - circularity_min) / circularity_range
        else:
            circularity_conf = 1.0

        # Area confidence (prefer mid-range holes)
        # Very small or very large holes are less confident
        min_area = self.config['min_area']
        max_area = self.config['max_area']
        mid_area = (min_area + max_area) / 2

        # Distance from ideal mid-range
        area_deviation = abs(area - mid_area) / mid_area
        area_conf = max(0.0, 1.0 - area_deviation)

        # Combine factors
        # Circularity is more important than size for hole detection
        confidence = 0.8 * circularity_conf + 0.2 * area_conf

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
