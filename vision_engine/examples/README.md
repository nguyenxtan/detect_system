# Vision Engine Examples

This directory contains example scripts demonstrating how to use the Vision Detection Engine.

## Examples

### 1. `basic_usage.py`

Basic inspection example showing:
- Configuration setup
- Single image inspection
- Result interpretation
- Output visualization

**Run:**
```bash
python basic_usage.py
```

**Prerequisites:**
- OpenCV, NumPy installed
- Test image (or will create synthetic)

---

### 2. `train_anomaly_detector.py`

Anomaly detector training example showing:
- Loading OK (defect-free) samples
- Training the memory bank
- Validation on test samples
- Saving/loading trained models

**Run:**
```bash
python train_anomaly_detector.py
```

**Prerequisites:**
- Collection of OK sample images in `ok_samples/` directory
- Or will use synthetic samples for demo

---

## Running Examples

All examples can run standalone with synthetic data for demonstration purposes.

For production use:
1. Replace synthetic data with actual images from your production line
2. Adjust configuration parameters in the scripts
3. Validate performance on labeled test set

## Custom Example Template

```python
import sys
from pathlib import Path
import cv2

# Add vision_engine to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vision_engine import VisionEngine, VisionConfig
from vision_engine.utils import draw_detections

# Create configuration
config = VisionConfig(
    enable_crack_detector=True,
    enable_hole_detector=True,
    anomaly_threshold=0.5
)

# Initialize engine
engine = VisionEngine(config)

# Inspect image
image = cv2.imread("your_image.jpg")
result = engine.inspect(image)

# Check result
print(f"Result: {result.result}")
if result.has_defects():
    for defect in result.defect_regions:
        print(f"Defect: {defect.defect_type} at ({defect.x}, {defect.y})")

# Visualize
annotated = draw_detections(image, result)
cv2.imwrite("output.jpg", annotated)
```
