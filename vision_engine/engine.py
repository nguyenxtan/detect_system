"""
Vision Detection Engine - Main inference API.

This is the primary interface for defect detection.
All detectors are coordinated through this engine.

Usage:
    from vision_engine import VisionEngine, VisionConfig

    # Create engine with configuration
    config = VisionConfig(
        anomaly_threshold=0.5,
        enable_crack_detector=True,
        enable_hole_detector=True
    )
    engine = VisionEngine(config)

    # Inspect image
    import cv2
    image = cv2.imread("sample.jpg")
    result = engine.inspect(image)

    # Check result
    if result.result == "NG":
        print(f"Defects found: {result.defect_count()}")
        for defect in result.defect_regions:
            print(f"  - {defect.defect_type} at ({defect.x}, {defect.y})")
"""

from typing import List, Optional
import time
import numpy as np
import cv2

from .types import InspectionResult, DefectRegion, VisionConfig
from .detectors import CrackDetector, HoleDetector, AnomalyDetector


class VisionEngine:
    """
    Main vision detection engine.

    Coordinates all detectors and produces final inspection results.

    Design:
    - Stateless: can process images independently
    - Configurable: all parameters via VisionConfig
    - Auditable: all decisions logged with metadata
    """

    def __init__(self, config: VisionConfig):
        """
        Initialize vision engine with configuration.

        Args:
            config: VisionConfig instance

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate configuration
        errors = config.validate()
        if errors:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")

        self.config = config
        self.detectors = []

        # Initialize enabled detectors
        self._initialize_detectors()

    def _initialize_detectors(self) -> None:
        """Initialize detector instances based on configuration."""
        # Crack detector
        if self.config.enable_crack_detector:
            crack_config = {
                'min_length': self.config.crack_min_length,
                'max_width': self.config.crack_max_width,
                'confidence_threshold': self.config.crack_confidence_threshold,
            }
            self.detectors.append(CrackDetector(crack_config))

        # Hole detector
        if self.config.enable_hole_detector:
            hole_config = {
                'min_area': self.config.hole_min_area,
                'max_area': self.config.hole_max_area,
                'circularity_threshold': self.config.hole_circularity_threshold,
            }
            self.detectors.append(HoleDetector(hole_config))

        # Anomaly detector
        if self.config.enable_anomaly_detector:
            anomaly_config = {
                'anomaly_threshold': self.config.anomaly_threshold,
            }
            self.anomaly_detector = AnomalyDetector(anomaly_config)
        else:
            self.anomaly_detector = None

        print(f"VisionEngine initialized with {len(self.detectors)} rule-based detectors")
        if self.anomaly_detector:
            print("  + Anomaly detector (requires training)")

    def inspect(
        self,
        image: np.ndarray,
        image_id: Optional[str] = None
    ) -> InspectionResult:
        """
        Inspect image for defects.

        SAFE ORCHESTRATION:
        1. Anomaly detector runs first (overall surface quality)
        2. Rule-based detectors run second (specific defect types)
        3. Results are merged and deduplicated
        4. Final OK/NG decision is made

        This method is SAFE and never raises exceptions.
        On critical errors, returns NG result with error logged.

        Args:
            image: Input image as numpy array (H, W, C) or (H, W)
            image_id: Optional identifier for audit trail

        Returns:
            InspectionResult with OK/NG decision and detected defects
        """
        start_time = time.time()

        try:
            # Validate image
            if not isinstance(image, np.ndarray):
                raise ValueError("Image must be numpy array")

            if image.size == 0:
                raise ValueError("Image is empty")

            # Preprocess if needed
            processed_image = self._preprocess_image(image)

            # STEP 1: Run anomaly detector first (if enabled)
            # This provides overall surface quality assessment
            anomaly_score = 0.0
            all_regions = []
            detector_names = []

            if self.anomaly_detector is not None:
                try:
                    anomaly_score = self.anomaly_detector.get_score(processed_image)
                    anomaly_regions = self.anomaly_detector.detect(processed_image)
                    all_regions.extend(anomaly_regions)
                    if anomaly_regions or anomaly_score > 0:
                        detector_names.append("AnomalyDetector")
                except Exception as e:
                    # Anomaly detector failed, but continue with rule-based detectors
                    import logging
                    logging.getLogger(__name__).error(f"Anomaly detector failed: {e}")
                    anomaly_score = 0.0

            # STEP 2: Run rule-based detectors second
            # These provide specific defect type identification
            for detector in self.detectors:
                try:
                    regions = detector.detect(processed_image)
                    all_regions.extend(regions)
                    if regions:
                        detector_names.append(detector.get_name())
                except Exception as e:
                    # Detector failed, log and continue with others
                    import logging
                    logging.getLogger(__name__).error(
                        f"{detector.get_name()} failed: {e}"
                    )
                    continue

            # STEP 3: Post-processing
            # Remove duplicate detections (non-maximum suppression)
            all_regions = self._remove_duplicates(all_regions)

            # Validate all regions are within image bounds
            h, w = processed_image.shape[:2]
            valid_regions = [r for r in all_regions if r.is_valid(w, h)]

            # STEP 4: Make OK/NG decision
            result = self._make_decision(anomaly_score, valid_regions)

            # Add metadata for audit trail
            processing_time = (time.time() - start_time) * 1000  # milliseconds
            result.processing_time_ms = processing_time
            result.image_id = image_id
            result.detectors_used = list(set(detector_names))
            result.anomaly_threshold = self.config.anomaly_threshold

            return result

        except Exception as e:
            # Critical error - return NG result with error logged
            import logging
            logging.getLogger(__name__).error(f"VisionEngine.inspect failed: {e}")

            # Return NG result (safe failure mode)
            processing_time = (time.time() - start_time) * 1000
            return InspectionResult.create_ng_result(
                anomaly_score=1.0,  # Assume defective on error
                defect_regions=[],
                metadata={
                    'image_id': image_id,
                    'processing_time_ms': processing_time,
                    'detectors_used': ['ERROR'],
                    'anomaly_threshold': self.config.anomaly_threshold
                }
            )

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image before detection.

        Args:
            image: Input image

        Returns:
            Preprocessed image
        """
        # Resize if configured
        if self.config.resize_width and self.config.resize_height:
            image = cv2.resize(
                image,
                (self.config.resize_width, self.config.resize_height)
            )

        return image

    def _remove_duplicates(self, regions: List[DefectRegion]) -> List[DefectRegion]:
        """
        Remove duplicate detections using non-maximum suppression.

        If multiple detectors find the same defect, keep the one with
        highest confidence.

        Args:
            regions: List of detected regions

        Returns:
            Filtered list with duplicates removed
        """
        if len(regions) <= 1:
            return regions

        # Simple NMS: if IoU > 0.5, keep higher confidence
        keep = []
        regions_sorted = sorted(regions, key=lambda r: r.confidence, reverse=True)

        for i, region in enumerate(regions_sorted):
            is_duplicate = False
            for kept_region in keep:
                iou = self._compute_iou(region, kept_region)
                if iou > 0.5:
                    is_duplicate = True
                    break

            if not is_duplicate:
                keep.append(region)

        return keep

    def _compute_iou(self, region1: DefectRegion, region2: DefectRegion) -> float:
        """
        Compute Intersection over Union (IoU) between two regions.

        Args:
            region1, region2: DefectRegion instances

        Returns:
            IoU value (0.0 to 1.0)
        """
        # Get coordinates
        x1_min, y1_min = region1.x, region1.y
        x1_max, y1_max = region1.x + region1.w, region1.y + region1.h

        x2_min, y2_min = region2.x, region2.y
        x2_max, y2_max = region2.x + region2.w, region2.y + region2.h

        # Intersection
        x_inter_min = max(x1_min, x2_min)
        y_inter_min = max(y1_min, y2_min)
        x_inter_max = min(x1_max, x2_max)
        y_inter_max = min(y1_max, y2_max)

        if x_inter_max <= x_inter_min or y_inter_max <= y_inter_min:
            return 0.0

        inter_area = (x_inter_max - x_inter_min) * (y_inter_max - y_inter_min)

        # Union
        area1 = region1.w * region1.h
        area2 = region2.w * region2.h
        union_area = area1 + area2 - inter_area

        if union_area == 0:
            return 0.0

        return inter_area / union_area

    def _make_decision(
        self,
        anomaly_score: float,
        regions: List[DefectRegion]
    ) -> InspectionResult:
        """
        Make final OK/NG decision based on detections.

        Decision logic:
        - NG if anomaly_score > threshold
        - NG if any rule-based detector found defects
        - OK otherwise

        Args:
            anomaly_score: Overall anomaly score
            regions: Detected defect regions

        Returns:
            InspectionResult with decision
        """
        # Check anomaly score
        if anomaly_score > self.config.anomaly_threshold:
            return InspectionResult.create_ng_result(
                anomaly_score=anomaly_score,
                defect_regions=regions
            )

        # Check if any defects detected
        if len(regions) > 0:
            return InspectionResult.create_ng_result(
                anomaly_score=anomaly_score,
                defect_regions=regions
            )

        # No defects found
        return InspectionResult.create_ok_result(
            anomaly_score=anomaly_score
        )

    def train_anomaly_detector(self, ok_images: List[np.ndarray]) -> None:
        """
        Train the anomaly detector on OK samples.

        This method must be called before deployment if anomaly
        detection is enabled.

        Args:
            ok_images: List of defect-free (OK) sample images

        Raises:
            RuntimeError: If anomaly detector is not enabled
            ValueError: If images are invalid
        """
        if self.anomaly_detector is None:
            raise RuntimeError("Anomaly detector not enabled in configuration")

        # Preprocess all images
        processed_images = [self._preprocess_image(img) for img in ok_images]

        # Train detector
        self.anomaly_detector.train(processed_images)

        print(f"Anomaly detector trained on {len(ok_images)} OK samples")

    def get_config(self) -> VisionConfig:
        """
        Get current configuration.

        Returns:
            VisionConfig instance
        """
        return self.config

    def get_detector_info(self) -> dict:
        """
        Get information about active detectors.

        Returns:
            Dictionary with detector information
        """
        info = {
            'num_rule_detectors': len(self.detectors),
            'rule_detectors': [d.get_name() for d in self.detectors],
            'anomaly_detector_enabled': self.anomaly_detector is not None,
            'anomaly_detector_trained': (
                self.anomaly_detector.is_trained
                if self.anomaly_detector else False
            ),
            'version': '2.0.0-alpha'
        }
        return info
