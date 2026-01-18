"""
Vision Engine Installation Verification Script

Run this script to verify that the vision engine is properly installed
and all dependencies are available.

Usage:
    python verify_installation.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_imports():
    """Verify all required modules can be imported."""
    print("Checking imports...")

    try:
        import numpy
        print("  ✓ numpy")
    except ImportError:
        print("  ✗ numpy - MISSING (install: pip install numpy)")
        return False

    try:
        import cv2
        print("  ✓ opencv-python")
    except ImportError:
        print("  ✗ opencv-python - MISSING (install: pip install opencv-python)")
        return False

    try:
        import yaml
        print("  ✓ pyyaml")
    except ImportError:
        print("  ✗ pyyaml - MISSING (install: pip install pyyaml)")
        return False

    return True


def verify_vision_engine():
    """Verify vision engine modules can be imported."""
    print("\nChecking vision engine modules...")

    try:
        from vision_engine import VisionEngine, VisionConfig
        print("  ✓ vision_engine.VisionEngine")
        print("  ✓ vision_engine.VisionConfig")
    except ImportError as e:
        print(f"  ✗ vision_engine - IMPORT ERROR: {e}")
        return False

    try:
        from vision_engine.types import InspectionResult, DefectRegion
        print("  ✓ vision_engine.types")
    except ImportError as e:
        print(f"  ✗ vision_engine.types - IMPORT ERROR: {e}")
        return False

    try:
        from vision_engine.detectors import CrackDetector, HoleDetector, AnomalyDetector
        print("  ✓ vision_engine.detectors")
    except ImportError as e:
        print(f"  ✗ vision_engine.detectors - IMPORT ERROR: {e}")
        return False

    try:
        from vision_engine.utils import draw_detections, load_config
        print("  ✓ vision_engine.utils")
    except ImportError as e:
        print(f"  ✗ vision_engine.utils - IMPORT ERROR: {e}")
        return False

    return True


def verify_functionality():
    """Verify basic functionality works."""
    print("\nChecking basic functionality...")

    try:
        from vision_engine import VisionEngine, VisionConfig
        import numpy as np

        # Create configuration
        config = VisionConfig(
            enable_crack_detector=True,
            enable_hole_detector=True,
            enable_anomaly_detector=False
        )
        print("  ✓ Configuration created")

        # Initialize engine
        engine = VisionEngine(config)
        print("  ✓ Engine initialized")

        # Create test image
        test_image = np.ones((600, 800, 3), dtype=np.uint8) * 200
        print("  ✓ Test image created")

        # Run inspection
        result = engine.inspect(test_image, image_id="TEST_001")
        print("  ✓ Inspection completed")

        # Verify result structure
        assert result.result in ["OK", "NG"]
        assert 0.0 <= result.anomaly_score <= 1.0
        assert isinstance(result.defect_regions, list)
        print("  ✓ Result structure valid")

        print(f"\n  Inspection result: {result.result}")
        print(f"  Anomaly score: {result.anomaly_score:.3f}")
        print(f"  Defects found: {result.defect_count()}")

        return True

    except Exception as e:
        print(f"  ✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("="*60)
    print("VISION ENGINE INSTALLATION VERIFICATION")
    print("="*60)

    # Check dependencies
    deps_ok = verify_imports()

    if not deps_ok:
        print("\n" + "="*60)
        print("RESULT: FAILED - Missing dependencies")
        print("="*60)
        print("\nInstall missing dependencies:")
        print("  pip install -r vision_engine/requirements.txt")
        return False

    # Check vision engine
    engine_ok = verify_vision_engine()

    if not engine_ok:
        print("\n" + "="*60)
        print("RESULT: FAILED - Vision engine import error")
        print("="*60)
        return False

    # Check functionality
    func_ok = verify_functionality()

    print("\n" + "="*60)
    if func_ok:
        print("RESULT: SUCCESS - Vision engine is ready to use!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Review vision_engine/README.md")
        print("  2. Run examples/basic_usage.py")
        print("  3. Collect production samples for validation")
        return True
    else:
        print("RESULT: FAILED - Functionality test failed")
        print("="*60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
