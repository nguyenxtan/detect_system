"""Machine Learning module"""
# Lazy import to avoid loading model at startup
# from .embeddings import EmbeddingService

# __all__ = ["EmbeddingService"]

def get_embedding_service():
    """Lazy load embedding service"""
    from .embeddings import EmbeddingService
    return EmbeddingService()

__all__ = ["get_embedding_service"]
