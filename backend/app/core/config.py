"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_SECRET_KEY: str
    API_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: str = ""

    # Storage
    UPLOAD_DIR: str = "./data/uploads"
    REFERENCE_DIR: str = "./data/reference_images"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # AI Model (CLIP)
    MODEL_NAME: str = "openai/clip-vit-base-patch32"
    SIMILARITY_THRESHOLD: float = 0.6
    IMAGE_WEIGHT: float = 0.6
    TEXT_WEIGHT: float = 0.4

    # Phase 3: Vision Pipeline
    ENABLE_VISION_PIPELINE: bool = False  # Enable two-stage detection
    VISION_MODEL_VERSION: str = "vision_engine_v0"
    VISION_ANOMALY_THRESHOLD: float = 0.5
    VISION_MATCH_ON_OK: bool = False  # If True, run CLIP matching even on OK results

    # CORS
    CORS_ORIGINS: str = "http://localhost:3001,http://localhost:3000"

    # Company
    COMPANY_NAME: str = "PU/PE Manufacturing"
    COMPANY_FOCUS: str = "Polyurethane (PU), Polyethylene (PE)"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @property
    def database_url(self) -> str:
        """Get database URL"""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
