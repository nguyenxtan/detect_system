"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .core.config import settings
from .core.database import engine, Base
from .api.endpoints import auth, defects, users

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Defect Recognition System",
    description="AI-assisted defect recognition for PU/PE manufacturing",
    version="1.0.0"
)

# CORS middleware
# ⚠️ Production: Chỉ cho phép origins cụ thể từ settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REFERENCE_DIR, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/references", StaticFiles(directory=settings.REFERENCE_DIR), name="references")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(defects.router, prefix="/defects", tags=["Defects"])
app.include_router(users.router, prefix="/users", tags=["Users"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Defect Recognition System API",
        "version": "1.0.0",
        "company": settings.COMPANY_NAME,
        "focus": settings.COMPANY_FOCUS
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
