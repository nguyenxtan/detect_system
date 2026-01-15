"""Embedding service using CLIP model"""
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
from typing import List, Tuple
import io
from ..core.config import settings


class EmbeddingService:
    """Service for generating embeddings using CLIP"""

    def __init__(self):
        """Initialize CLIP model"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP model on {self.device}...")
        try:
            self.model = CLIPModel.from_pretrained(settings.MODEL_NAME).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(settings.MODEL_NAME)
            self.model.eval()
            print("CLIP model loaded successfully")
        except Exception as e:
            print(f"Warning: Failed to load CLIP model: {e}")
            print("Continuing without AI features...")
            self.model = None
            self.processor = None

    def get_image_embedding(self, image_data: bytes) -> np.ndarray:
        """
        Generate embedding from image bytes

        Args:
            image_data: Image data in bytes

        Returns:
            Normalized embedding vector
        """
        image = Image.open(io.BytesIO(image_data)).convert("RGB")

        with torch.no_grad():
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            image_features = self.model.get_image_features(**inputs)
            # Normalize
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features.cpu().numpy()[0]

    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding from text

        Args:
            text: Input text

        Returns:
            Normalized embedding vector
        """
        with torch.no_grad():
            inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
            text_features = self.model.get_text_features(**inputs)
            # Normalize
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy()[0]

    def get_text_embedding_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts

        Returns:
            Array of normalized embedding vectors
        """
        with torch.no_grad():
            inputs = self.processor(text=texts, return_tensors="pt", padding=True).to(self.device)
            text_features = self.model.get_text_features(**inputs)
            # Normalize
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy()

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1)
        """
        # Debug logging
        if embedding1 is None:
            print(f"❌ ERROR: embedding1 is None!")
            return 0.0
        if embedding2 is None:
            print(f"❌ ERROR: embedding2 is None!")
            return 0.0

        print(f"[DEBUG] embedding1 type: {type(embedding1)}, shape: {embedding1.shape if hasattr(embedding1, 'shape') else 'no shape'}")
        print(f"[DEBUG] embedding2 type: {type(embedding2)}, shape: {embedding2.shape if hasattr(embedding2, 'shape') else 'no shape'}")

        similarity = np.dot(embedding1, embedding2)
        return float(similarity)

    def find_best_match(
        self,
        image_embedding: np.ndarray,
        text_query: str,
        candidate_profiles: List[dict]
    ) -> Tuple[dict, float]:
        """
        Find best matching defect profile

        Args:
            image_embedding: Image embedding from user
            text_query: Optional text query
            candidate_profiles: List of defect profiles with embeddings

        Returns:
            Best matching profile and confidence score
        """
        best_match = None
        best_score = 0.0

        print(f"\n[MATCHING] Comparing against {len(candidate_profiles)} profiles...")
        print(f"[MATCHING] Weights: IMAGE={settings.IMAGE_WEIGHT}, TEXT={settings.TEXT_WEIGHT}")

        for idx, profile in enumerate(candidate_profiles):
            # Image similarity
            img_sim = self.compute_similarity(
                image_embedding,
                np.array(profile['image_embedding'])
            )

            # Text similarity (if text_query provided)
            if text_query and profile.get('text_embedding'):
                text_emb = self.get_text_embedding(text_query)
                text_sim = self.compute_similarity(
                    text_emb,
                    np.array(profile['text_embedding'])
                )
                # Weighted score when both image and text available
                final_score = (
                    settings.IMAGE_WEIGHT * img_sim +
                    settings.TEXT_WEIGHT * text_sim
                )
            else:
                text_sim = 0.0
                # Use 100% image similarity when no text query
                final_score = img_sim

            # Get profile info
            prof_obj = profile.get('profile')
            prof_name = f"{prof_obj.customer}-{prof_obj.part_code}-{prof_obj.defect_type}" if prof_obj else "Unknown"

            print(f"[MATCHING] Profile {idx+1}: {prof_name}")
            print(f"           Image sim: {img_sim:.4f}, Text sim: {text_sim:.4f}, Final: {final_score:.4f}")

            if final_score > best_score:
                best_score = final_score
                best_match = profile

        print(f"\n[MATCHING] Best score: {best_score:.4f}")
        print(f"[MATCHING] Threshold: {settings.SIMILARITY_THRESHOLD}")

        return best_match, best_score


# Global instance - will be initialized lazily
embedding_service = None

def get_embedding_service_instance():
    """Get or create embedding service instance"""
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service
