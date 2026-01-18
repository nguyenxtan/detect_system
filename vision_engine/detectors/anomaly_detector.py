"""
Anomaly Detector using memory-bank approach (PatchCore/PaDiM concept).

Concept:
- Build a memory bank of "normal" (OK) image features during training
- At inference, compare test image features to memory bank
- High distance = anomalous = potential defect

This is a SKELETON implementation for Phase 2.
Full implementation requires:
- Feature extraction (e.g., pretrained CNN like ResNet)
- Memory bank construction from OK samples
- Efficient nearest-neighbor search
- Anomaly score aggregation

Current implementation:
- Provides interface and structure
- Uses simple statistical baseline (mean/std deviation)
- Can be extended with proper feature extraction

Production deployment requires:
- Collection of "golden sample" OK images
- Memory bank training phase
- Validation on known defects
- Threshold tuning for target false positive rate
"""

from typing import List, Optional
import numpy as np
import cv2
from .base import BaseDetector
from ..types import DefectRegion


class AnomalyDetector(BaseDetector):
    """
    Anomaly detector using statistical baseline approach.

    This is a simplified implementation. Production deployment
    should use proper feature extraction (e.g., pretrained ResNet).

    Parameters:
        anomaly_threshold: Anomaly score threshold (default: 0.5)
        patch_size: Size of patches for local analysis (default: 32)
        stride: Stride for patch extraction (default: 16)

    Training requirements:
        - Collection of 50-200 OK (defect-free) samples
        - Representative of normal production variation
        - Same lighting and camera conditions as deployment
    """

    def __init__(self, config: dict):
        """Initialize anomaly detector."""
        super().__init__(config)
        self.memory_bank = None  # Will store reference features
        self.is_trained = False

    def validate_config(self) -> None:
        """Validate anomaly detector configuration."""
        if 'anomaly_threshold' not in self.config:
            raise ValueError("Missing required config: anomaly_threshold")

        threshold = self.config['anomaly_threshold']
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("anomaly_threshold must be between 0.0 and 1.0")

    def train(self, ok_images: List[np.ndarray]) -> None:
        """
        Train the anomaly detector on OK (defect-free) samples.

        This method should be called before deployment with a
        representative set of good samples.

        Args:
            ok_images: List of OK sample images (same size)

        Raises:
            ValueError: If images are invalid or inconsistent
        """
        if len(ok_images) == 0:
            raise ValueError("Need at least 1 OK sample for training")

        print(f"Training anomaly detector on {len(ok_images)} OK samples...")

        # Extract features from all OK samples
        all_features = []
        for img in ok_images:
            features = self._extract_features(img)
            all_features.append(features)

        # Build memory bank (simple: store mean and std)
        # Production: should store actual feature vectors for k-NN
        all_features = np.array(all_features)
        self.memory_bank = {
            'mean': np.mean(all_features, axis=0),
            'std': np.std(all_features, axis=0) + 1e-6,  # Avoid division by zero
            'num_samples': len(ok_images)
        }

        self.is_trained = True
        print(f"Training complete. Memory bank: {all_features.shape}")

    def detect(self, image: np.ndarray) -> List[DefectRegion]:
        """
        Detect anomalous regions in the image.

        SAFE FAILURE: Never raises exceptions. Returns empty list on any error.

        This method returns anomalous regions only if anomaly score
        exceeds threshold. For overall anomaly score, use get_score().

        Args:
            image: Input image

        Returns:
            List of anomalous regions (empty list if error or no anomalies)
        """
        try:
            if not self.is_trained:
                # Untrained detector returns no localized anomalies
                # (but get_score() can still return baseline score)
                return []

            # Validate image
            if not self._validate_image(image):
                return []

            # Get anomaly map (spatial anomaly scores)
            anomaly_map = self._compute_anomaly_map(image)

            # Find regions with high anomaly scores
            regions = self._localize_anomalies(anomaly_map)

            return regions

        except Exception as e:
            # Log error but do not crash
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AnomalyDetector.detect failed: {e}")
            return []

    def get_score(self, image: np.ndarray) -> float:
        """
        Get overall anomaly score for the image.

        SAFE FAILURE: Never raises exceptions. Returns 0.0 on any error.

        This is the primary output for OK/NG decision.
        Overrides BaseDetector.get_score() with anomaly-specific logic.

        Args:
            image: Input image

        Returns:
            Anomaly score (0.0 = normal, 1.0 = highly anomalous)
        """
        try:
            if not self.is_trained:
                # Untrained: assume OK (return 0.0)
                return 0.0

            if not self._validate_image(image):
                return 0.0

            # Extract features
            features = self._extract_features(image)

            # Compute anomaly score (distance from normal)
            score = self._compute_anomaly_score(features)

            return score

        except Exception as e:
            # Log error but do not crash
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AnomalyDetector.get_score failed: {e}")
            return 0.0

    def get_anomaly_score(self, image: np.ndarray) -> float:
        """
        DEPRECATED: Use get_score() instead.

        This method is kept for backward compatibility but delegates to get_score().

        Args:
            image: Input image

        Returns:
            Anomaly score (0.0 = normal, 1.0 = highly anomalous)
        """
        import warnings
        warnings.warn(
            "get_anomaly_score() is deprecated. Use get_score() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_score(image)

    def _extract_features(self, image: np.ndarray) -> np.ndarray:
        """
        Extract features from image.

        PLACEHOLDER: This should use a pretrained CNN (e.g., ResNet)
        for production deployment.

        Current implementation: Simple statistical features for baseline.

        Args:
            image: Input image

        Returns:
            Feature vector
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Resize to standard size for consistency
        gray = cv2.resize(gray, (256, 256))

        # Extract simple statistical features as baseline
        # Production should use CNN features (e.g., ResNet layer outputs)
        features = []

        # Global statistics
        features.append(np.mean(gray))
        features.append(np.std(gray))
        features.append(np.min(gray))
        features.append(np.max(gray))

        # Histogram features (8 bins)
        hist, _ = np.histogram(gray, bins=8, range=(0, 256))
        hist = hist / (hist.sum() + 1e-6)  # Normalize
        features.extend(hist)

        # Texture features (simple)
        # Gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        features.append(np.mean(grad_mag))
        features.append(np.std(grad_mag))

        return np.array(features)

    def _compute_anomaly_score(self, features: np.ndarray) -> float:
        """
        Compute anomaly score from features.

        Uses Mahalanobis-like distance from normal distribution.

        Args:
            features: Feature vector

        Returns:
            Anomaly score (0.0 to 1.0)
        """
        if self.memory_bank is None:
            return 0.0

        mean = self.memory_bank['mean']
        std = self.memory_bank['std']

        # Compute normalized distance (z-score)
        z_score = np.abs((features - mean) / std)

        # Aggregate to single score (max deviation)
        max_z = np.max(z_score)

        # Map to 0-1 range (z-score of 3 -> score of 1.0)
        score = min(1.0, max_z / 3.0)

        return score

    def _compute_anomaly_map(self, image: np.ndarray) -> np.ndarray:
        """
        Compute spatial anomaly map.

        PLACEHOLDER: Production should use patch-based CNN features.

        Args:
            image: Input image

        Returns:
            Anomaly map (same size as image, values 0-1)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        h, w = gray.shape

        # Simple baseline: use gradient magnitude as proxy for anomaly
        # Production should use patch-wise feature comparison
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)

        # Normalize to 0-1
        grad_mag = (grad_mag - grad_mag.min()) / (grad_mag.max() - grad_mag.min() + 1e-6)

        return grad_mag.astype(np.float32)

    def _localize_anomalies(self, anomaly_map: np.ndarray) -> List[DefectRegion]:
        """
        Find regions with high anomaly scores.

        Args:
            anomaly_map: Spatial anomaly scores

        Returns:
            List of anomalous regions
        """
        threshold = self.config['anomaly_threshold']

        # Threshold anomaly map
        binary = (anomaly_map > threshold).astype(np.uint8) * 255

        # Find connected components
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        regions = []
        min_area = self.config.get('min_anomaly_area', 100)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Get mean anomaly score in this region
            mask = np.zeros(anomaly_map.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            region_scores = anomaly_map[mask == 255]
            confidence = float(np.mean(region_scores))

            # Create defect region
            region = self._create_defect_region(
                x=x,
                y=y,
                w=w,
                h=h,
                confidence=confidence,
                defect_type="anomaly"
            )
            regions.append(region)

        return regions

    def save_memory_bank(self, filepath: str) -> None:
        """
        Save trained memory bank to file.

        Args:
            filepath: Path to save file (.npz format)
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained detector")

        np.savez(
            filepath,
            mean=self.memory_bank['mean'],
            std=self.memory_bank['std'],
            num_samples=self.memory_bank['num_samples']
        )
        print(f"Memory bank saved to {filepath}")

    def load_memory_bank(self, filepath: str) -> None:
        """
        Load trained memory bank from file.

        Args:
            filepath: Path to saved file (.npz format)
        """
        data = np.load(filepath)
        self.memory_bank = {
            'mean': data['mean'],
            'std': data['std'],
            'num_samples': int(data['num_samples'])
        }
        self.is_trained = True
        print(f"Memory bank loaded from {filepath}")
