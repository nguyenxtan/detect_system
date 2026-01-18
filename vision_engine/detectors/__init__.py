"""
Defect detector modules.

Each detector is independent and can be enabled/disabled via configuration.
All detectors follow the same interface for consistency.
"""

from .base import BaseDetector
from .crack_detector import CrackDetector
from .hole_detector import HoleDetector
from .anomaly_detector import AnomalyDetector

__all__ = [
    "BaseDetector",
    "CrackDetector",
    "HoleDetector",
    "AnomalyDetector",
]
