"""
Minimal tests for image utilities (Phase 3 integration)

Tests focus on critical safety requirements:
- Bounds clamping works correctly
- No crashes on invalid inputs
- Crop returns None on errors (safe failure)
"""

import numpy as np
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.image_utils import clamp_box, crop_defect_region, select_best_region


def test_clamp_box_within_bounds():
    """Test that valid box is unchanged"""
    x, y, w, h = clamp_box(10, 10, 50, 50, 100, 100)
    assert x == 10
    assert y == 10
    assert w == 50
    assert h == 50
    print("✓ test_clamp_box_within_bounds passed")


def test_clamp_box_exceeds_bounds():
    """Test that box exceeding bounds is clamped"""
    # Box extends beyond image width
    x, y, w, h = clamp_box(80, 10, 50, 50, 100, 100)
    assert x == 80
    assert y == 10
    assert w == 20  # Clamped to fit within image
    assert h == 50
    print("✓ test_clamp_box_exceeds_bounds passed")


def test_clamp_box_negative_coords():
    """Test that negative coordinates are clamped to 0"""
    x, y, w, h = clamp_box(-10, -5, 50, 50, 100, 100)
    assert x == 0  # Clamped to 0
    assert y == 0  # Clamped to 0
    assert w == 50
    assert h == 50
    print("✓ test_clamp_box_negative_coords passed")


def test_crop_valid_region():
    """Test successful crop of valid region"""
    # Create test image
    image = np.ones((100, 100, 3), dtype=np.uint8) * 255

    # Crop valid region
    cropped = crop_defect_region(image, 10, 10, 30, 30)

    assert cropped is not None
    assert cropped.shape == (30, 30, 3)
    print("✓ test_crop_valid_region passed")


def test_crop_with_padding():
    """Test crop with padding"""
    image = np.ones((100, 100, 3), dtype=np.uint8) * 255

    # Crop with 5px padding
    cropped = crop_defect_region(image, 20, 20, 20, 20, padding=5)

    assert cropped is not None
    # Original: 20x20, with padding: 30x30 (5px on each side)
    assert cropped.shape == (30, 30, 3)
    print("✓ test_crop_with_padding passed")


def test_crop_out_of_bounds_returns_none_or_clamped():
    """Test that out-of-bounds crop is handled safely"""
    image = np.ones((100, 100, 3), dtype=np.uint8) * 255

    # Try to crop beyond image bounds
    cropped = crop_defect_region(image, 90, 90, 50, 50)

    # Should return clamped region or None (both safe)
    if cropped is not None:
        # If clamped, should be 10x10 (remaining space)
        assert cropped.shape[0] <= 10
        assert cropped.shape[1] <= 10
    print("✓ test_crop_out_of_bounds handled safely")


def test_crop_empty_image_returns_none():
    """Test that empty image returns None"""
    image = np.array([])

    cropped = crop_defect_region(image, 0, 0, 10, 10)

    assert cropped is None
    print("✓ test_crop_empty_image_returns_none passed")


def test_crop_none_image_returns_none():
    """Test that None image returns None"""
    cropped = crop_defect_region(None, 0, 0, 10, 10)

    assert cropped is None
    print("✓ test_crop_none_image_returns_none passed")


def test_select_best_region_largest():
    """Test selection of largest region"""
    regions = [
        {"x": 0, "y": 0, "w": 10, "h": 10, "confidence": 0.9},  # area = 100
        {"x": 0, "y": 0, "w": 20, "h": 20, "confidence": 0.7},  # area = 400 (largest)
        {"x": 0, "y": 0, "w": 5, "h": 5, "confidence": 0.95},   # area = 25
    ]

    best = select_best_region(regions, strategy="largest")

    assert best["w"] == 20
    assert best["h"] == 20
    print("✓ test_select_best_region_largest passed")


def test_select_best_region_highest_confidence():
    """Test selection by highest confidence"""
    regions = [
        {"x": 0, "y": 0, "w": 10, "h": 10, "confidence": 0.9},
        {"x": 0, "y": 0, "w": 20, "h": 20, "confidence": 0.7},
        {"x": 0, "y": 0, "w": 5, "h": 5, "confidence": 0.95},  # highest
    ]

    best = select_best_region(regions, strategy="highest_confidence")

    assert best["confidence"] == 0.95
    print("✓ test_select_best_region_highest_confidence passed")


def test_select_best_region_empty_returns_none():
    """Test that empty list returns None"""
    best = select_best_region([], strategy="largest")

    assert best is None
    print("✓ test_select_best_region_empty_returns_none passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 3 IMAGE UTILS TESTS")
    print("="*60 + "\n")

    tests = [
        test_clamp_box_within_bounds,
        test_clamp_box_exceeds_bounds,
        test_clamp_box_negative_coords,
        test_crop_valid_region,
        test_crop_with_padding,
        test_crop_out_of_bounds_returns_none_or_clamped,
        test_crop_empty_image_returns_none,
        test_crop_none_image_returns_none,
        test_select_best_region_largest,
        test_select_best_region_highest_confidence,
        test_select_best_region_empty_returns_none,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
