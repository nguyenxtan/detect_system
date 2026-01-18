
# Defect Recognition & Description System
## Technical Specification (AI-assisted Coding)

---

## 1. System Positioning & Overview

### 1.1 What This System Is

This system is a **Defect Knowledge Base and Decision Support Tool** for Quality Control operations in PE/PU manufacturing environments.

The system supports **defect recognition and standardized defect description** for industrial products.

**Key Positioning:**
- A knowledge management system for defect descriptions
- A decision support tool for QC staff
- NOT a pixel-level vision inspection system
- NOT an automated OK/NG production line system

### 1.2 Decision Support Architecture

Instead of fully autonomous AI classification, the system follows a **Decision Support Architecture**:

- Human-defined defect knowledge base (QC-standard descriptions)
- AI-assisted matching (image + text similarity)
- Telegram bot interface for real users
- Full defect history logging for traceability and future training

### 1.3 Current Scope (Phase 1)

**What the system does:**
- Stores QC-approved defect profiles with reference images
- Matches user-submitted images to known defect profiles
- Returns standardized defect descriptions
- Maintains full audit trail

**What the system does NOT do (in current phase):**
- Automated defect detection on production lines
- Pixel-level defect localization
- Automatic OK/NG decisions
- Real-time vision inspection

---

## 2. Core Objectives

1. Allow admins to define defect profiles (based on Excel + reference images)
2. Allow users to submit defect images via Telegram
3. Match user images to the most relevant defect profile
4. Return standardized QC defect descriptions
5. Store all defect cases for audit, search, and future model training

---

## 3. System Architecture

```

[Web Admin Portal]

* Create / edit Defect Profiles
* Upload reference images
* Define standardized descriptions

  ```
  ↓ (store)
  ```

[Defect Knowledge Base]

* PostgreSQL + pgvector
* Object Storage (images)

  ```
  ↓ (query)
  ```

[AI Engine]

* Image embedding
* Text embedding
* Similarity matching
* Optional classifier

  ```
  ↓
  ```

[Telegram Bot]

* Receives defect images
* Returns defect description + confidence
* Allows history search

````

---

## 4. Defect Knowledge Base (Core Concept)

Each row from the Excel file represents **one Defect Profile**.

### 4.1 Defect Profile Fields

```json
{
  "id": "uuid",
  "customer": "FAPV",
  "part_code": "GD3346",
  "part_name": "Grommet",
  "defect_type": "can | rach | nhan | phong | ok",
  "defect_title": "Cấn",
  "defect_description": "Trên bề mặt sản phẩm xuất hiện vết lõm kéo dài...",
  "keywords": ["can", "vet lom", "ep", "gap"],
  "severity": "minor | major | critical",
  "reference_images": ["img1.jpg", "img2.jpg"],
  "image_embedding": "vector",
  "text_embedding": "vector",
  "created_at": "timestamp"
}
````

---

## 5. Website (Admin / QC Portal)

### 5.1 Purpose

* Replace Excel as structured input
* Create trusted QC-standard defect descriptions
* Provide reference images for AI matching

### 5.2 Features

* CRUD Defect Profiles
* Upload multiple reference images per defect
* Auto-generate embeddings on save
* Role-based access (admin / qc)

### 5.3 Tech Stack

* Frontend: React / Vue
* Backend: FastAPI
* Auth: JWT / session
* Storage: S3-compatible (MinIO)

---

## 6. Telegram Bot

### 6.1 User Flow

1. User sends defect image
2. Bot acknowledges receipt
3. AI Engine processes image
4. Bot returns:

   * Defect name
   * Standardized description
   * Reference image
   * Similarity score (%)

### 6.2 Commands

```
/start           → bot intro
/report          → submit defect image
/history         → last 10 defects
/detail <id>     → view defect case
/search <text>   → search defect history
```

---

## 7. AI Engine Design

### 7.1 Phase 1 – Similarity Matching (No Training Required)

#### Image Processing

* Use CLIP / ViT image encoder
* Generate image embedding
* Normalize vector

#### Text Processing

* Use same model text encoder
* Encode defect descriptions + keywords

#### Matching Logic

```python
final_score = 0.6 * image_similarity + 0.4 * text_similarity
```

Return top-1 or top-3 defect profiles.

---

### 7.2 Phase 2 – Lightweight Training (Optional, Future)

When dataset grows:

* Train defect type classifier:

  * Input: image
  * Output: defect_type
* Use transfer learning (MobileNet / EfficientNet)

Pipeline:

```
Classifier → filter KB by defect_type → similarity matching
```

---

## 8. Data Storage

### 8.1 Defect Incidents Table

```sql
defect_incidents (
  id UUID,
  user_id TEXT,
  defect_profile_id UUID,
  predicted_defect_type TEXT,
  confidence FLOAT,
  image_url TEXT,
  model_version TEXT,
  created_at TIMESTAMP
)
```

### 8.2 Vector Storage

* pgvector or FAISS
* Separate tables for image and text embeddings

---

## 9. Deployment

### 9.1 Initial Deployment (No GPU)

* 2–4 vCPU
* 8GB RAM
* CPU inference (CLIP)

### 9.2 Scaling

* Add GPU when YOLO / segmentation is introduced
* Use async task queue if load increases

---

## 10. Model Governance & Audit

* Always store model_version
* Never overwrite historical results
* Allow human correction (feedback loop)
* Use feedback for retraining

---

## 11. Design Principles

* AI supports QC, does not replace QC
* Human-defined knowledge is source of truth
* Explainable results over black-box prediction
* Incremental AI adoption

---

## 12. Development Roadmap

### Phase 1: Defect Knowledge Base (Current - Deployed)

**Status:** Operational

**Implementation:**
- Defect profile CRUD via web admin portal
- CLIP-based image and text embedding generation
- Vector similarity matching using pgvector
- Telegram bot interface for defect reporting
- Full audit trail for all defect incidents

**Use Case:** Post-inspection knowledge management, QC training, defect standardization.

---

### Phase 2: Vision Detection Engine (Planned)

**Objective:** Add automated defect detection capabilities for PE/PU surfaces.

**Planned Capabilities:**
- Anomaly detection for surface irregularities
- Defect localization with bounding boxes or segmentation
- Defect classification (crack, bubble, hole, scratch, etc.)
- OK/NG decision support
- Rule-based vision for configurable defect criteria

**Technical Implementation:**
- Anomaly detection: PatchCore, FastFlow, or similar
- Object detection: YOLOv8, Faster R-CNN
- Segmentation: U-Net, Mask R-CNN
- Model fine-tuning on PE/PU manufacturing dataset
- GPU acceleration for real-time inference
- Edge deployment for production line integration

**Deployment Considerations:**
- Separate from Phase 1 initially (independent operation)
- Requires GPU infrastructure
- Performance benchmarks for speed and accuracy
- Configurable sensitivity and thresholds

---

### Phase 3: Integrated Vision + Knowledge System (Planned)

**Objective:** Combine automated defect detection with standardized QC knowledge.

**Integrated Architecture:**

```
[Vision Engine] → Detect defect region → Extract ROI
       ↓
[Knowledge Base] → Match ROI to reference profiles → Return standardized description
       ↓
[Audit System] → Log detection + description + confidence
```

**Benefits:**
- Automated detection with human-readable explanations
- Consistent defect terminology across automated and manual inspection
- Full traceability: detection logic + description matching
- Continuous improvement via feedback loop

**Technical Integration:**
- Vision engine provides defect ROI coordinates
- Knowledge system performs similarity matching on ROI
- Combined confidence: Detection confidence × Description match score
- Unified API for detection and knowledge retrieval

**Deployment Architecture:**
- Vision engine: Edge inference (production line)
- Knowledge system: Centralized server (cross-site knowledge sharing)
- Hybrid mode: Local detection + cloud knowledge lookup

**Governance:**
- QC override and correction capabilities
- Feedback loop updates knowledge base
- Model versioning and rollback
- A/B testing framework

---

## 13. Design Principles (Applies to All Phases)

* **AI supports QC, does not replace QC** - Final decisions remain with trained personnel
* **Explainability over accuracy** - QC must understand system recommendations
* **Incremental adoption** - Start simple, add complexity only when needed
* **Traceability and auditability** - Every decision traceable to source data and model version
* **Human-in-the-loop** - QC knowledge is the source of truth

---

## End of Specification

**Document Version:** 1.1
**Last Updated:** 2026-01-18
**System Type:** Defect Knowledge & Decision Support (Not Vision Inspection)

```