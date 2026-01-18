"""
Visualization utilities for inspection results.

These functions are for:
- QC review and verification
- Training material generation
- Audit report creation
"""

from typing import List, Tuple
import numpy as np
import cv2
from ..types import InspectionResult, DefectRegion


# Color definitions (BGR format for OpenCV)
COLOR_OK = (0, 255, 0)      # Green
COLOR_NG = (0, 0, 255)      # Red
COLOR_CRACK = (255, 0, 255)  # Magenta
COLOR_HOLE = (0, 165, 255)   # Orange
COLOR_ANOMALY = (0, 255, 255) # Yellow

DEFECT_COLORS = {
    'crack': COLOR_CRACK,
    'hole': COLOR_HOLE,
    'anomaly': COLOR_ANOMALY,
}


def draw_detections(
    image: np.ndarray,
    result: InspectionResult,
    show_confidence: bool = True,
    line_thickness: int = 2
) -> np.ndarray:
    """
    Draw detection results on image.

    Args:
        image: Input image (will not be modified)
        result: InspectionResult to visualize
        show_confidence: Whether to show confidence scores
        line_thickness: Thickness of bounding boxes

    Returns:
        New image with detections drawn
    """
    # Create copy to avoid modifying original
    output = image.copy()

    # Ensure color image
    if len(output.shape) == 2:
        output = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)

    # Draw each defect region
    for region in result.defect_regions:
        color = DEFECT_COLORS.get(region.defect_type, (255, 255, 255))

        # Draw bounding box
        pt1 = (region.x, region.y)
        pt2 = (region.x + region.w, region.y + region.h)
        cv2.rectangle(output, pt1, pt2, color, line_thickness)

        # Draw label
        label = region.defect_type
        if show_confidence:
            label += f" {region.confidence:.2f}"

        # Background for text
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(
            output,
            (region.x, region.y - text_h - 4),
            (region.x + text_w, region.y),
            color,
            -1
        )

        # Text
        cv2.putText(
            output,
            label,
            (region.x, region.y - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),  # Black text
            1
        )

    return output


def create_report_image(
    image: np.ndarray,
    result: InspectionResult,
    include_metadata: bool = True
) -> np.ndarray:
    """
    Create a comprehensive report image for QC review.

    Includes:
    - Original image with detections
    - Metadata panel with inspection details

    Args:
        image: Input image
        result: InspectionResult
        include_metadata: Whether to include metadata panel

    Returns:
        Report image
    """
    # Draw detections
    annotated = draw_detections(image, result)

    if not include_metadata:
        return annotated

    # Create metadata panel
    h, w = annotated.shape[:2]
    panel_height = 150
    panel = np.ones((panel_height, w, 3), dtype=np.uint8) * 240  # Light gray

    # Add text information
    y_offset = 25
    line_height = 25

    # Overall result
    result_color = COLOR_NG if result.result == "NG" else COLOR_OK
    cv2.putText(
        panel,
        f"Result: {result.result}",
        (10, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        result_color,
        2
    )

    # Anomaly score
    y_offset += line_height
    cv2.putText(
        panel,
        f"Anomaly Score: {result.anomaly_score:.3f}",
        (10, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 0),
        1
    )

    # Defect count
    y_offset += line_height
    cv2.putText(
        panel,
        f"Defects Found: {result.defect_count()}",
        (10, y_offset),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 0),
        1
    )

    # Defects by type
    if result.has_defects():
        y_offset += line_height
        defects_by_type = result.defects_by_type()
        defect_str = ", ".join([f"{k}: {v}" for k, v in defects_by_type.items()])
        cv2.putText(
            panel,
            f"Types: {defect_str}",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1
        )

    # Processing time
    if result.processing_time_ms:
        y_offset += line_height
        cv2.putText(
            panel,
            f"Processing: {result.processing_time_ms:.1f} ms",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1
        )

    # Combine image and panel
    report = np.vstack([annotated, panel])

    return report


def save_detection_overlay(
    image: np.ndarray,
    result: InspectionResult,
    output_path: str
) -> None:
    """
    Save image with detection overlay.

    Args:
        image: Input image
        result: InspectionResult
        output_path: Path to save output image
    """
    report = create_report_image(image, result, include_metadata=True)
    cv2.imwrite(output_path, report)


def draw_anomaly_heatmap(
    image: np.ndarray,
    anomaly_map: np.ndarray,
    alpha: float = 0.5
) -> np.ndarray:
    """
    Overlay anomaly heatmap on image.

    Args:
        image: Input image
        anomaly_map: Anomaly scores (0-1) same size as image
        alpha: Transparency (0=transparent, 1=opaque)

    Returns:
        Image with heatmap overlay
    """
    # Ensure color image
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Resize anomaly map if needed
    h, w = image.shape[:2]
    if anomaly_map.shape[:2] != (h, w):
        anomaly_map = cv2.resize(anomaly_map, (w, h))

    # Convert anomaly scores to heatmap
    # Blue (low) -> Green (medium) -> Red (high)
    heatmap = (anomaly_map * 255).astype(np.uint8)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # Blend with original image
    output = cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)

    return output
