"""
Image utility functions for vision pipeline integration.

Phase 3: Safe image cropping with bounds clamping.
"""

import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def clamp_box(x: int, y: int, w: int, h: int, image_width: int, image_height: int) -> Tuple[int, int, int, int]:
    """
    Clamp bounding box to image bounds.

    Args:
        x, y: Top-left corner
        w, h: Width and height
        image_width, image_height: Image dimensions

    Returns:
        Clamped (x, y, w, h) tuple
    """
    # Clamp x, y to be within image
    x = max(0, min(x, image_width - 1))
    y = max(0, min(y, image_height - 1))

    # Adjust width and height to not exceed image bounds
    max_w = image_width - x
    max_h = image_height - y
    w = max(1, min(w, max_w))
    h = max(1, min(h, max_h))

    return x, y, w, h


def crop_defect_region(
    image: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    padding: int = 0
) -> Optional[np.ndarray]:
    """
    Crop defect region from image with safe bounds clamping.

    Args:
        image: Input image (H, W, C) or (H, W)
        x, y: Top-left corner of defect region
        w, h: Width and height of region
        padding: Optional padding around region (pixels)

    Returns:
        Cropped image region, or None if invalid

    Safety guarantees:
        - Never crashes on out-of-bounds coordinates
        - Always clamps to valid image bounds
        - Returns None if region is invalid (e.g., zero area)
    """
    try:
        if image is None or image.size == 0:
            logger.warning("Cannot crop from empty or None image")
            return None

        image_height, image_width = image.shape[:2]

        # Apply padding
        if padding > 0:
            x = x - padding
            y = y - padding
            w = w + 2 * padding
            h = h + 2 * padding

        # Clamp to image bounds
        x, y, w, h = clamp_box(x, y, w, h, image_width, image_height)

        # Validate final region
        if w <= 0 or h <= 0:
            logger.warning(f"Invalid crop region after clamping: w={w}, h={h}")
            return None

        # Crop
        x2 = x + w
        y2 = y + h
        cropped = image[y:y2, x:x2]

        if cropped.size == 0:
            logger.warning(f"Crop resulted in empty image: region ({x},{y},{w},{h})")
            return None

        return cropped

    except Exception as e:
        logger.error(f"Failed to crop region ({x},{y},{w},{h}): {e}")
        return None


def select_best_region(defect_regions: List[dict], strategy: str = "largest") -> Optional[dict]:
    """
    Select the best defect region from a list.

    Args:
        defect_regions: List of defect region dicts with keys: x, y, w, h, confidence, etc.
        strategy: Selection strategy:
            - "largest": Select region with largest area (default)
            - "highest_confidence": Select region with highest confidence
            - "first": Select first region (simplest)

    Returns:
        Selected region dict, or None if list is empty

    Phase 3 default: "largest" area
    Can be extended later with more sophisticated strategies.
    """
    if not defect_regions:
        return None

    if strategy == "first":
        return defect_regions[0]

    elif strategy == "highest_confidence":
        return max(defect_regions, key=lambda r: r.get("confidence", 0.0))

    elif strategy == "largest":
        # Default: select region with largest area
        def get_area(region: dict) -> int:
            w = region.get("w", 0)
            h = region.get("h", 0)
            return w * h

        return max(defect_regions, key=get_area)

    else:
        logger.warning(f"Unknown strategy '{strategy}', using 'largest'")
        return select_best_region(defect_regions, strategy="largest")
