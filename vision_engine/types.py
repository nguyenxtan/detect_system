"""
Data types and structures for Vision Detection Engine.

All types are designed for:
- JSON serialization (API responses)
- Audit trail storage
- QC report generation
- Consistency across all modules

Type Aliases:
- BoundingBox = DefectRegion (for clarity)
- Both names refer to the same structure
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Literal
from datetime import datetime


@dataclass
class DefectRegion:
    """
    Represents a detected defect region in the image.

    Also known as: BoundingBox (same structure, different terminology)

    Coordinates are in pixels, origin at top-left.
    All coordinates must be validated to be within image bounds.
    """
    x: int  # Top-left X coordinate
    y: int  # Top-left Y coordinate
    w: int  # Width in pixels
    h: int  # Height in pixels
    defect_type: str  # e.g., "crack", "hole", "anomaly"
    confidence: float  # 0.0 to 1.0
    detector_name: str  # Which detector found this (for traceability)

    def __post_init__(self):
        """Validate field types and ranges after initialization."""
        # Ensure coordinates are integers
        self.x = int(self.x)
        self.y = int(self.y)
        self.w = int(self.w)
        self.h = int(self.h)

        # Ensure confidence is float in valid range
        self.confidence = float(self.confidence)
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")

        # Ensure defect_type and detector_name are strings
        if not isinstance(self.defect_type, str) or not self.defect_type:
            raise ValueError("defect_type must be non-empty string")

        if not isinstance(self.detector_name, str) or not self.detector_name:
            raise ValueError("detector_name must be non-empty string")


    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def area(self) -> int:
        """Calculate defect region area in pixels."""
        return self.w * self.h

    def is_valid(self, image_width: int, image_height: int) -> bool:
        """Validate that region is within image bounds."""
        if self.x < 0 or self.y < 0:
            return False
        if self.w <= 0 or self.h <= 0:
            return False
        if self.x + self.w > image_width:
            return False
        if self.y + self.h > image_height:
            return False
        return True


@dataclass
class InspectionResult:
    """
    Complete inspection result for a single image.

    This structure is designed to be:
    - Stored in audit database
    - Returned via REST API
    - Included in QC reports
    """
    result: Literal["OK", "NG"]  # Pass/Fail decision
    anomaly_score: float  # 0.0 (perfect) to 1.0 (highly anomalous)
    defect_regions: List[DefectRegion]  # List of detected defects

    # Metadata for audit trail
    timestamp: str  # ISO 8601 format
    image_id: Optional[str] = None  # Reference to source image
    model_version: str = "2.0.0-alpha"  # Vision engine version

    # Processing information
    processing_time_ms: Optional[float] = None
    detectors_used: Optional[List[str]] = None  # List of active detectors

    # Decision thresholds used (for explainability)
    anomaly_threshold: Optional[float] = None
    min_defect_area: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert defect_regions to list of dicts
        data['defect_regions'] = [dr.to_dict() for dr in self.defect_regions]
        return data

    def defect_count(self) -> int:
        """Total number of defects detected."""
        return len(self.defect_regions)

    def has_defects(self) -> bool:
        """Check if any defects were detected."""
        return len(self.defect_regions) > 0

    def defects_by_type(self) -> dict:
        """Count defects grouped by type."""
        counts = {}
        for region in self.defect_regions:
            defect_type = region.defect_type
            counts[defect_type] = counts.get(defect_type, 0) + 1
        return counts

    @staticmethod
    def create_ok_result(anomaly_score: float, metadata: dict = None) -> "InspectionResult":
        """
        Factory method for OK (pass) results.

        Args:
            anomaly_score: Anomaly score (should be below threshold)
            metadata: Optional metadata to include

        Returns:
            InspectionResult with OK status
        """
        return InspectionResult(
            result="OK",
            anomaly_score=anomaly_score,
            defect_regions=[],
            timestamp=datetime.utcnow().isoformat() + "Z",
            **(metadata or {})
        )

    @staticmethod
    def create_ng_result(
        anomaly_score: float,
        defect_regions: List[DefectRegion],
        metadata: dict = None
    ) -> "InspectionResult":
        """
        Factory method for NG (fail) results.

        Args:
            anomaly_score: Anomaly score (typically above threshold)
            defect_regions: List of detected defects
            metadata: Optional metadata to include

        Returns:
            InspectionResult with NG status
        """
        return InspectionResult(
            result="NG",
            anomaly_score=anomaly_score,
            defect_regions=defect_regions,
            timestamp=datetime.utcnow().isoformat() + "Z",
            **(metadata or {})
        )


@dataclass
class VisionConfig:
    """
    Configuration for Vision Detection Engine.

    All parameters should be:
    - Documented with physical meaning
    - Validated on load
    - Logged with inspection results
    """
    # Anomaly detection parameters
    anomaly_threshold: float = 0.5  # Score above this = NG

    # Rule-based detector parameters
    enable_crack_detector: bool = True
    enable_hole_detector: bool = True
    enable_anomaly_detector: bool = True

    # Crack detector settings
    crack_min_length: int = 20  # pixels
    crack_max_width: int = 5    # pixels
    crack_confidence_threshold: float = 0.7

    # Hole detector settings
    hole_min_area: int = 50     # square pixels
    hole_max_area: int = 5000   # square pixels
    hole_circularity_threshold: float = 0.6  # 0-1, higher = more circular

    # Image preprocessing
    resize_width: Optional[int] = None  # None = use original size
    resize_height: Optional[int] = None

    # Performance
    use_gpu: bool = False  # Phase 2 is CPU-only

    def validate(self) -> List[str]:
        """
        Validate configuration parameters.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not 0.0 <= self.anomaly_threshold <= 1.0:
            errors.append("anomaly_threshold must be between 0.0 and 1.0")

        if self.crack_min_length <= 0:
            errors.append("crack_min_length must be positive")

        if self.hole_min_area <= 0:
            errors.append("hole_min_area must be positive")

        if self.hole_max_area < self.hole_min_area:
            errors.append("hole_max_area must be >= hole_min_area")

        if not 0.0 <= self.hole_circularity_threshold <= 1.0:
            errors.append("hole_circularity_threshold must be between 0.0 and 1.0")

        return errors


# Type aliases for API clarity
# BoundingBox and DefectRegion are the same type
BoundingBox = DefectRegion
