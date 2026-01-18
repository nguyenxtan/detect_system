# Vision Detection Engine

**Phase 2: Automated Defect Detection for PE/PU Surfaces**

---

## Overview

The Vision Detection Engine provides automated defect detection capabilities for polyurethane (PU) and polyethylene (PE) manufacturing surfaces. This module operates **independently** from the Phase 1 Defect Knowledge Base and will be integrated in Phase 3.

### Design Philosophy

This engine is designed according to industrial quality control principles:

- **Explainability First** - Every detection must be traceable to specific visual features
- **Conservative Detection** - Prefer false positives (NG when OK) over false negatives (OK when NG)
- **Auditable** - All parameters, thresholds, and decisions are logged
- **Configurable** - QC staff can tune detection sensitivity without code changes
- **CPU-First** - Optimized for CPU deployment; GPU support can be added later

---

## What This Module Does

### Current Capabilities (Phase 2)

1. **Anomaly Detection**
   - Detects surface irregularities that deviate from normal appearance
   - Uses memory-bank approach (inspired by PatchCore/PaDiM)
   - Requires training on defect-free (OK) samples
   - Returns overall anomaly score (0.0 = normal, 1.0 = highly anomalous)

2. **Rule-Based Crack Detection**
   - Detects thin, elongated dark regions characteristic of cracks
   - Uses edge detection + morphological operations + contour analysis
   - Configurable minimum length and maximum width
   - Returns bounding boxes and confidence scores

3. **Rule-Based Hole/Void Detection**
   - Detects circular or elliptical dark regions (holes, voids, bubbles)
   - Uses intensity thresholding + circularity analysis
   - Configurable size range and shape criteria
   - Returns bounding boxes and confidence scores

4. **Standardized Inference API**
   - Input: image (numpy array)
   - Output: `InspectionResult` with OK/NG decision, defect regions, confidence scores
   - Full audit trail metadata included

### What This Module Does NOT Do (Yet)

- Does NOT integrate with defect knowledge base (Phase 3)
- Does NOT provide QC-standard descriptions (Phase 3)
- Does NOT use GPU acceleration (can be added as optimization)
- Does NOT perform real-time video stream processing
- Does NOT handle defect classification beyond crack/hole/anomaly

---

## Architecture

### Module Structure

```
vision_engine/
├── __init__.py              # Public API
├── types.py                 # Data structures (InspectionResult, DefectRegion, VisionConfig)
├── engine.py                # Main VisionEngine class
├── detectors/
│   ├── __init__.py
│   ├── base.py              # BaseDetector abstract class
│   ├── crack_detector.py    # Rule-based crack detection
│   ├── hole_detector.py     # Rule-based hole detection
│   └── anomaly_detector.py  # Anomaly detection (memory-bank)
├── utils/
│   ├── __init__.py
│   ├── visualization.py     # Draw detections, create reports
│   └── config_loader.py     # YAML configuration management
└── config/
    └── default_config.yaml  # Default parameters
```

### Detection Pipeline

```
Input Image
    ↓
Preprocessing (resize, normalize)
    ↓
┌─────────────────────────────────────┐
│   Parallel Detection                │
│   ├─ Crack Detector                 │
│   ├─ Hole Detector                  │
│   └─ Anomaly Detector                │
└─────────────────────────────────────┘
    ↓
Non-Maximum Suppression (remove duplicates)
    ↓
OK/NG Decision
    ↓
InspectionResult (with audit metadata)
```

### Key Design Choices

#### 1. Anomaly Detection Approach

**Why Memory-Bank (PatchCore-style)?**

- **No training data required initially** - Can work with small sets of OK samples
- **Explainable** - Anomaly is defined as "different from normal," which QC staff understand
- **Unsupervised** - Doesn't require labeled defects, only OK samples
- **Handles novel defects** - Can detect defect types not seen during training

**Current Implementation:**
- Simple statistical baseline using image features (mean, std, histogram, gradients)
- Designed as skeleton for future enhancement with CNN features (e.g., ResNet embeddings)

**Production Enhancement Path:**
1. Replace feature extraction with pretrained CNN (e.g., ResNet-18, EfficientNet)
2. Use patch-based features instead of global features
3. Implement efficient k-NN search (e.g., FAISS)
4. Generate spatial anomaly maps for localization

#### 2. Rule-Based Detectors

**Why Rules Instead of Deep Learning?**

For crack and hole detection, rule-based methods are chosen because:

- **Explainable** - QC can see exactly why a defect was flagged (e.g., "elongated dark region 50px long")
- **No training data needed** - Works immediately without labeled datasets
- **Tunable** - QC staff can adjust thresholds based on acceptance criteria
- **Deterministic** - Same image always produces same result (important for audits)
- **Fast** - CPU-based OpenCV operations are very efficient

**Limitations:**
- May have higher false positive rate on textured surfaces
- Cannot handle complex defect patterns
- Requires manual threshold tuning

**When to Upgrade to Deep Learning:**
- When > 1000 labeled defect samples are available
- When false positive rate exceeds QC tolerance
- When defect types become too complex for rules

#### 3. CPU-First Design

**Why Not GPU?**

Phase 2 is designed for CPU deployment because:

- **Lower deployment cost** - No GPU hardware required
- **Easier integration** - Works on standard servers or edge devices
- **Sufficient performance** - Current detectors run < 200ms per image on modern CPUs
- **Simpler maintenance** - No GPU driver or CUDA compatibility issues

**GPU Migration Path:**
- Add GPU support as configuration flag (`use_gpu: true`)
- Implement GPU-accelerated feature extraction (PyTorch/TensorFlow)
- Keep CPU path as fallback

#### 4. Standardized Output Format

All detections follow the same `InspectionResult` structure:

```python
{
  "result": "OK" | "NG",
  "anomaly_score": 0.0-1.0,
  "defect_regions": [
    {
      "x": int, "y": int, "w": int, "h": int,
      "defect_type": "crack" | "hole" | "anomaly",
      "confidence": 0.0-1.0,
      "detector_name": str
    }
  ],
  "timestamp": "ISO8601",
  "processing_time_ms": float,
  "model_version": "2.0.0-alpha"
}
```

This enables:
- Database storage for audit trail
- API integration (FastAPI/REST)
- QC report generation
- Model performance tracking

---

## Usage

### Basic Usage

```python
from vision_engine import VisionEngine, VisionConfig
import cv2

# 1. Create configuration
config = VisionConfig(
    anomaly_threshold=0.5,
    enable_crack_detector=True,
    enable_hole_detector=True,
    enable_anomaly_detector=False  # Requires training
)

# 2. Initialize engine
engine = VisionEngine(config)

# 3. Inspect image
image = cv2.imread("sample_part.jpg")
result = engine.inspect(image, image_id="PART_12345")

# 4. Check result
if result.result == "NG":
    print(f"DEFECT DETECTED: {result.defect_count()} defects found")
    for defect in result.defect_regions:
        print(f"  - {defect.defect_type} at ({defect.x}, {defect.y}), "
              f"confidence: {defect.confidence:.2f}")
else:
    print(f"OK: No defects detected (anomaly score: {result.anomaly_score:.3f})")
```

### Training Anomaly Detector

```python
import cv2
import glob

# 1. Collect OK samples (defect-free parts)
ok_image_paths = glob.glob("ok_samples/*.jpg")
ok_images = [cv2.imread(p) for p in ok_image_paths]

print(f"Collected {len(ok_images)} OK samples for training")

# 2. Initialize engine with anomaly detector enabled
config = VisionConfig(
    enable_anomaly_detector=True,
    anomaly_threshold=0.5
)
engine = VisionEngine(config)

# 3. Train
engine.train_anomaly_detector(ok_images)

# 4. Save trained model (for deployment)
# engine.anomaly_detector.save_memory_bank("models/anomaly_memory_bank.npz")

# 5. Test on new image
test_image = cv2.imread("test_sample.jpg")
result = engine.inspect(test_image)
print(f"Anomaly score: {result.anomaly_score}")
```

### Loading Configuration from YAML

```python
from vision_engine.utils import load_config
from vision_engine import VisionEngine

# Load from custom config
config = load_config("config/production_config.yaml")
engine = VisionEngine(config)

# Inspect
result = engine.inspect(image)
```

### Visualization

```python
from vision_engine.utils import draw_detections, create_report_image
import cv2

# Inspect image
result = engine.inspect(image)

# Draw detections
annotated = draw_detections(image, result, show_confidence=True)
cv2.imwrite("output_annotated.jpg", annotated)

# Create full report with metadata
report = create_report_image(image, result, include_metadata=True)
cv2.imwrite("output_report.jpg", report)
```

---

## Configuration Guide

### Configuration Parameters

All parameters are defined in `config/default_config.yaml` and can be customized.

#### Anomaly Detection

```yaml
anomaly_threshold: 0.5  # Score above this = NG
enable_anomaly_detector: true
```

**Tuning:**
- **Increase threshold (0.6-0.8)** - Reduce false positives, may miss subtle defects
- **Decrease threshold (0.3-0.4)** - Catch more defects, may increase false positives
- Requires validation on labeled test set

#### Crack Detector

```yaml
enable_crack_detector: true
crack_min_length: 20      # Minimum crack length in pixels
crack_max_width: 5        # Maximum crack width in pixels
crack_confidence_threshold: 0.7
```

**Tuning:**
- **Increase `crack_min_length`** - Ignore small scratches, reduce false positives on texture
- **Increase `crack_max_width`** - Detect wider cracks (may catch non-cracks)
- **Decrease `crack_confidence_threshold`** - More sensitive, may increase false positives

**Pixel-to-Real-World Conversion:**
- Measure actual crack dimensions on sample parts
- Calculate pixels per mm based on camera resolution and field of view
- Set thresholds in pixels accordingly

Example: If 1mm = 10 pixels, and minimum critical crack is 2mm → set `crack_min_length: 20`

#### Hole Detector

```yaml
enable_hole_detector: true
hole_min_area: 50         # Minimum area in square pixels
hole_max_area: 5000       # Maximum area in square pixels
hole_circularity_threshold: 0.6  # 0.0-1.0, higher = more circular
```

**Tuning:**
- **Adjust `hole_min_area` / `hole_max_area`** - Based on acceptable hole sizes per QC standards
- **Increase `hole_circularity_threshold`** - Only detect very circular holes
- **Decrease threshold** - Detect irregular voids and bubbles

**Area Calculation:**
- If hole diameter = 2mm and 1mm = 10 pixels → diameter = 20 pixels → area = π × 10² ≈ 314 square pixels

#### Image Preprocessing

```yaml
resize_width: null   # null = use original size
resize_height: null
```

**When to Resize:**
- High-resolution images (> 2000px) may slow processing
- Resizing to 800-1000px width usually sufficient for defect detection
- Maintain aspect ratio
- Test detection performance after resizing

---

## Validation and Threshold Tuning

### Validation Process

1. **Collect Validation Dataset**
   - 50-100 labeled images: OK and NG (with defect types marked)
   - Representative of production variation (lighting, angles, part variation)
   - Include edge cases (borderline defects, textured surfaces)

2. **Baseline Evaluation**
   - Run engine with default configuration
   - Calculate metrics:
     - False Positive Rate (FPR): NG predictions on OK samples
     - False Negative Rate (FNR): OK predictions on NG samples
     - Precision, Recall, F1 for each defect type

3. **Threshold Tuning**
   - Adjust thresholds to meet QC requirements
   - Example: "FPR must be < 5%, FNR must be < 1%"
   - Document all changes

4. **Re-validation**
   - Test with updated configuration
   - Verify metrics meet requirements
   - Get QC approval

5. **Production Deployment**
   - Freeze configuration
   - Version control the config file
   - Monitor performance on production data

### Metrics Tracking

```python
from vision_engine import VisionEngine
from vision_engine.utils import load_config
import cv2

# Load validation data
validation_data = [
    {"image_path": "val_001.jpg", "label": "OK"},
    {"image_path": "val_002.jpg", "label": "NG", "defect_type": "crack"},
    # ... more samples
]

# Initialize engine
config = load_config("config/production_config.yaml")
engine = VisionEngine(config)

# Evaluate
correct = 0
false_positives = 0
false_negatives = 0

for sample in validation_data:
    image = cv2.imread(sample["image_path"])
    result = engine.inspect(image)

    if result.result == sample["label"]:
        correct += 1
    elif result.result == "NG" and sample["label"] == "OK":
        false_positives += 1
    elif result.result == "OK" and sample["label"] == "NG":
        false_negatives += 1

accuracy = correct / len(validation_data)
fpr = false_positives / len([s for s in validation_data if s["label"] == "OK"])
fnr = false_negatives / len([s for s in validation_data if s["label"] == "NG"])

print(f"Accuracy: {accuracy:.2%}")
print(f"False Positive Rate: {fpr:.2%}")
print(f"False Negative Rate: {fnr:.2%}")
```

---

## Deployment Considerations

### System Requirements

**Minimum:**
- CPU: 2 cores, 2.0 GHz
- RAM: 4 GB
- OS: Linux, Windows, macOS

**Recommended:**
- CPU: 4+ cores, 3.0 GHz
- RAM: 8 GB
- SSD storage

**Performance:**
- Crack detector: ~30-50ms per image (800x600)
- Hole detector: ~40-60ms per image
- Anomaly detector (baseline): ~60-80ms per image
- **Total: ~150-200ms per image on modern CPU**

### Integration Options

#### Option 1: Standalone Service

Run as HTTP API:

```python
from fastapi import FastAPI, File, UploadFile
from vision_engine import VisionEngine, VisionConfig
import cv2
import numpy as np

app = FastAPI()
engine = VisionEngine(VisionConfig())

@app.post("/inspect")
async def inspect_image(file: UploadFile = File(...)):
    # Read image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Inspect
    result = engine.inspect(image, image_id=file.filename)

    # Return JSON
    return result.to_dict()
```

#### Option 2: Batch Processing

Process images from folder:

```python
import glob
import cv2
from vision_engine import VisionEngine, VisionConfig

engine = VisionEngine(VisionConfig())

image_paths = glob.glob("input/*.jpg")
for path in image_paths:
    image = cv2.imread(path)
    result = engine.inspect(image, image_id=path)

    # Save result
    if result.result == "NG":
        # Copy to NG folder
        # Log to database
        pass
```

#### Option 3: Edge Deployment

Deploy on edge device near production line:

- Package as Docker container
- Include config and trained models
- Expose REST API for PLC or MES integration
- Store results locally with periodic sync to central server

---

## Extending the Engine

### Adding a New Detector

1. **Create detector class** inheriting from `BaseDetector`:

```python
from .base import BaseDetector
from ..types import DefectRegion
import numpy as np

class BubbleDetector(BaseDetector):
    def validate_config(self):
        # Validate parameters
        pass

    def detect(self, image: np.ndarray):
        # Implement detection logic
        # Return list of DefectRegion
        pass
```

2. **Register in `detectors/__init__.py`**

3. **Add configuration parameters to `VisionConfig`**

4. **Initialize in `VisionEngine._initialize_detectors()`**

### Upgrading Anomaly Detector

To use CNN features instead of statistical baseline:

```python
# Replace _extract_features() in anomaly_detector.py
import torch
from torchvision.models import resnet18

def _extract_features(self, image: np.ndarray):
    # Use pretrained ResNet
    model = resnet18(pretrained=True)
    model.eval()

    # Extract features from layer3 (or layer4)
    # Return feature vector
    pass
```

### Adding GPU Support

```python
# In engine.py or detector
import torch

if self.config.use_gpu and torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
```

---

## Troubleshooting

### High False Positive Rate

**Symptoms:** Many OK parts flagged as NG

**Solutions:**
1. Increase detection thresholds
2. Train anomaly detector on more diverse OK samples
3. Add preprocessing (denoising, normalization)
4. Review lighting conditions for consistency

### High False Negative Rate

**Symptoms:** Defective parts pass inspection

**Solutions:**
1. Decrease detection thresholds
2. Add more sensitive detectors
3. Improve image quality (resolution, lighting)
4. Collect more defect samples for validation

### Slow Processing

**Symptoms:** > 500ms per image

**Solutions:**
1. Resize images to smaller resolution
2. Disable unused detectors
3. Optimize anomaly detector (use GPU, reduce feature dimension)
4. Profile code to find bottlenecks

### Inconsistent Results

**Symptoms:** Same image produces different results

**Solutions:**
1. Check if lighting or camera position changed
2. Ensure image preprocessing is consistent
3. Verify configuration hasn't changed
4. Check if anomaly detector memory bank is loaded correctly

---

## Audit and Compliance

### Traceability

Every `InspectionResult` includes:
- Timestamp (ISO 8601 format)
- Image ID reference
- Model version
- All detection parameters used
- Processing time

Store in database for full audit trail:

```sql
CREATE TABLE inspection_results (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    image_id TEXT,
    result TEXT,  -- OK or NG
    anomaly_score FLOAT,
    defect_count INT,
    model_version TEXT,
    config_snapshot JSONB  -- Store config used
);
```

### Version Control

- All configuration files in git
- Tag releases: `v2.0.0-alpha`, `v2.0.1-beta`
- Document all threshold changes with justification
- Link to validation reports

### Change Management

When updating thresholds or configuration:

1. Document reason for change
2. Run validation on test set
3. Get QC approval
4. Version bump
5. Deploy with rollback plan

---

## Roadmap (Phase 2 → Phase 3)

### Phase 2 Current State
✅ Rule-based crack and hole detection
✅ Anomaly detection skeleton
✅ Standardized output format
✅ Configuration management
✅ Visualization tools

### Phase 3 Integration (Planned)

**Objective:** Combine Vision Detection Engine with Defect Knowledge Base

**Integration Points:**
1. Vision engine detects defect region (bounding box)
2. Crop defect region from image
3. Send cropped region to Phase 1 knowledge base
4. Knowledge base returns standardized QC description
5. Combine: Detection + Description in unified result

**Benefits:**
- Automated detection (Phase 2) + Human-readable description (Phase 1)
- Consistent QC language
- Full traceability: "What was detected" + "How it was described"

---

## Support and Contribution

For questions or issues:
- Review this README
- Check configuration in `config/default_config.yaml`
- Validate installation: `python -c "from vision_engine import VisionEngine; print('OK')"`

---

**Module Version:** 2.0.0-alpha
**Last Updated:** 2026-01-18
**Module Type:** Automated Defect Detection (Phase 2)
**Not Integrated With:** Defect Knowledge Base (integration in Phase 3)
