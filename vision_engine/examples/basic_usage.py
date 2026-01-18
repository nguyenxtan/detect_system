"""
Basic usage example for Vision Detection Engine.

This script demonstrates:
1. Creating a vision engine with configuration
2. Inspecting a single image
3. Displaying results
4. Saving annotated output
"""

import sys
import cv2
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vision_engine import VisionEngine, VisionConfig
from vision_engine.utils import draw_detections, create_report_image


def main():
    """Run basic inspection example."""

    # Step 1: Create configuration
    print("Step 1: Creating vision engine configuration...")
    config = VisionConfig(
        # Enable detectors
        enable_crack_detector=True,
        enable_hole_detector=True,
        enable_anomaly_detector=False,  # Requires training

        # Crack detector settings
        crack_min_length=20,
        crack_max_width=5,
        crack_confidence_threshold=0.7,

        # Hole detector settings
        hole_min_area=50,
        hole_max_area=5000,
        hole_circularity_threshold=0.6,

        # Decision threshold
        anomaly_threshold=0.5,
    )

    # Validate configuration
    errors = config.validate()
    if errors:
        print(f"Configuration errors: {errors}")
        return

    print("  ✓ Configuration created")

    # Step 2: Initialize engine
    print("\nStep 2: Initializing vision engine...")
    engine = VisionEngine(config)
    print("  ✓ Engine initialized")
    print(f"  Active detectors: {engine.get_detector_info()}")

    # Step 3: Load test image
    print("\nStep 3: Loading test image...")

    # IMPORTANT: Replace with actual image path
    image_path = "test_sample.jpg"

    # For demonstration, create a synthetic test image if no file provided
    if not Path(image_path).exists():
        print(f"  Warning: {image_path} not found, creating synthetic test image...")
        image = create_synthetic_test_image()
    else:
        image = cv2.imread(image_path)

    if image is None:
        print(f"  Error: Could not load image")
        return

    print(f"  ✓ Image loaded: {image.shape}")

    # Step 4: Inspect image
    print("\nStep 4: Running inspection...")
    result = engine.inspect(image, image_id="DEMO_001")
    print(f"  ✓ Inspection complete in {result.processing_time_ms:.1f} ms")

    # Step 5: Display results
    print("\n" + "="*50)
    print("INSPECTION RESULTS")
    print("="*50)
    print(f"Overall Result: {result.result}")
    print(f"Anomaly Score:  {result.anomaly_score:.3f}")
    print(f"Defects Found:  {result.defect_count()}")

    if result.has_defects():
        print("\nDetected Defects:")
        for i, defect in enumerate(result.defect_regions, 1):
            print(f"  {i}. {defect.defect_type.upper()}")
            print(f"     Location: ({defect.x}, {defect.y})")
            print(f"     Size: {defect.w} x {defect.h} pixels")
            print(f"     Confidence: {defect.confidence:.2f}")
            print(f"     Detected by: {defect.detector_name}")
    else:
        print("\nNo defects detected - part is OK")

    # Step 6: Save annotated output
    print("\n" + "="*50)
    print("SAVING OUTPUTS")
    print("="*50)

    # Save detection overlay
    annotated = draw_detections(image, result, show_confidence=True)
    output_path = "output_annotated.jpg"
    cv2.imwrite(output_path, annotated)
    print(f"  ✓ Annotated image saved: {output_path}")

    # Save full report
    report = create_report_image(image, result, include_metadata=True)
    report_path = "output_report.jpg"
    cv2.imwrite(report_path, report)
    print(f"  ✓ Report image saved: {report_path}")

    print("\nDone!")


def create_synthetic_test_image():
    """
    Create a synthetic test image with defects for demonstration.

    Returns:
        Test image (numpy array)
    """
    import numpy as np

    # Create gray background
    image = np.ones((600, 800, 3), dtype=np.uint8) * 200

    # Add a crack-like feature (dark elongated region)
    cv2.line(image, (100, 100), (300, 120), (50, 50, 50), 3)

    # Add a hole-like feature (dark circle)
    cv2.circle(image, (500, 300), 30, (30, 30, 30), -1)

    # Add noise
    noise = np.random.randint(-20, 20, image.shape, dtype=np.int16)
    image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return image


if __name__ == "__main__":
    main()
