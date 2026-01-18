"""
Vision Detection Engine for PE/PU Surface Defect Inspection

This module provides automated defect detection capabilities for
polyurethane (PU) and polyethylene (PE) manufacturing surfaces.

Phase 2 Implementation:
- Anomaly detection for surface irregularities
- Rule-based OpenCV detectors for specific defect types
- Standardized inference API

NOT included in Phase 2:
- Integration with defect knowledge base (Phase 3)
- GPU optimization (can be added later)
- Real-time production line deployment

Design Principles:
- Explainability: Every detection must be traceable
- Conservative: Prefer false positives over false negatives
- Auditable: All parameters and thresholds configurable and logged
"""

__version__ = "2.0.0-alpha"
__author__ = "PU/PE Manufacturing QC Team"

from .engine import VisionEngine
from .types import InspectionResult, DefectRegion, BoundingBox

__all__ = ["VisionEngine", "InspectionResult", "DefectRegion", "BoundingBox"]
