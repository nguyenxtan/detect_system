"""
Example: Training the anomaly detector on OK samples.

This script demonstrates:
1. Collecting OK (defect-free) samples
2. Training the anomaly detector
3. Testing on new samples
4. Saving the trained model
"""

import sys
import cv2
import glob
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vision_engine import VisionEngine, VisionConfig


def main():
    """Train anomaly detector on OK samples."""

    print("="*60)
    print("ANOMALY DETECTOR TRAINING")
    print("="*60)

    # Step 1: Collect OK samples
    print("\nStep 1: Collecting OK (defect-free) samples...")

    # IMPORTANT: Replace with actual path to OK samples
    ok_samples_path = "ok_samples/*.jpg"

    ok_image_paths = glob.glob(ok_samples_path)

    if len(ok_image_paths) == 0:
        print(f"  Warning: No OK samples found at {ok_samples_path}")
        print("  Creating synthetic OK samples for demonstration...")
        ok_images = [create_synthetic_ok_sample() for _ in range(20)]
    else:
        ok_images = [cv2.imread(p) for p in ok_image_paths]
        ok_images = [img for img in ok_images if img is not None]

    print(f"  ✓ Collected {len(ok_images)} OK samples")

    if len(ok_images) < 10:
        print("\n  ⚠ Warning: < 10 samples may not be sufficient")
        print("  Recommended: 50-200 samples for production deployment")

    # Step 2: Create configuration
    print("\nStep 2: Creating configuration...")
    config = VisionConfig(
        enable_anomaly_detector=True,
        anomaly_threshold=0.5,
        enable_crack_detector=False,  # Disable for this example
        enable_hole_detector=False,
    )
    print("  ✓ Configuration created")

    # Step 3: Initialize engine
    print("\nStep 3: Initializing vision engine...")
    engine = VisionEngine(config)
    print("  ✓ Engine initialized")

    # Step 4: Train anomaly detector
    print("\nStep 4: Training anomaly detector...")
    print(f"  Training on {len(ok_images)} samples...")

    try:
        engine.train_anomaly_detector(ok_images)
        print("  ✓ Training complete!")
    except Exception as e:
        print(f"  ✗ Training failed: {e}")
        return

    # Step 5: Validate on OK samples
    print("\nStep 5: Validating on training samples...")
    ok_scores = []
    for i, img in enumerate(ok_images[:10]):  # Test on first 10
        result = engine.inspect(img, image_id=f"OK_{i}")
        ok_scores.append(result.anomaly_score)

    avg_ok_score = sum(ok_scores) / len(ok_scores)
    max_ok_score = max(ok_scores)

    print(f"  Average OK score: {avg_ok_score:.3f}")
    print(f"  Max OK score:     {max_ok_score:.3f}")
    print(f"  Current threshold: {config.anomaly_threshold:.3f}")

    if max_ok_score > config.anomaly_threshold:
        print(f"\n  ⚠ Warning: Some OK samples exceed threshold!")
        print(f"  Consider increasing threshold to {max_ok_score + 0.1:.2f}")

    # Step 6: Test on defective sample (if available)
    print("\nStep 6: Testing on defective sample...")

    # Create synthetic defective sample for demo
    defect_image = create_synthetic_defect_sample()
    result = engine.inspect(defect_image, image_id="DEFECT_001")

    print(f"  Result: {result.result}")
    print(f"  Anomaly score: {result.anomaly_score:.3f}")

    if result.result == "NG":
        print("  ✓ Defect correctly detected!")
    else:
        print("  ✗ Defect not detected - may need threshold adjustment")

    # Step 7: Save trained model
    print("\nStep 7: Saving trained model...")
    model_path = "anomaly_memory_bank.npz"

    try:
        engine.anomaly_detector.save_memory_bank(model_path)
        print(f"  ✓ Model saved: {model_path}")
    except Exception as e:
        print(f"  ✗ Save failed: {e}")

    # Step 8: Demonstrate loading model
    print("\nStep 8: Demonstrating model loading...")

    # Create new engine
    new_engine = VisionEngine(config)

    try:
        new_engine.anomaly_detector.load_memory_bank(model_path)
        print(f"  ✓ Model loaded successfully")

        # Test that loaded model works
        test_result = new_engine.inspect(ok_images[0])
        print(f"  Test score with loaded model: {test_result.anomaly_score:.3f}")

    except Exception as e:
        print(f"  ✗ Load failed: {e}")

    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Collect more OK samples (target: 50-200)")
    print("2. Validate on labeled test set (OK + NG samples)")
    print("3. Tune anomaly_threshold based on validation results")
    print("4. Deploy trained model to production")


def create_synthetic_ok_sample():
    """Create a synthetic OK (defect-free) sample."""
    import numpy as np

    # Create clean gray surface with slight texture
    image = np.ones((600, 800, 3), dtype=np.uint8) * 200

    # Add subtle texture
    noise = np.random.randint(-10, 10, image.shape, dtype=np.int16)
    image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return image


def create_synthetic_defect_sample():
    """Create a synthetic defective sample."""
    import numpy as np

    # Create base image
    image = create_synthetic_ok_sample()

    # Add a defect (large dark spot)
    cv2.circle(image, (400, 300), 50, (100, 100, 100), -1)

    # Add scratch
    cv2.line(image, (200, 200), (500, 250), (80, 80, 80), 3)

    return image


if __name__ == "__main__":
    main()
