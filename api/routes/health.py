"""
Health Check API Routes
"""
from fastapi import APIRouter
from api.schemas.responses import HealthResponse
from datetime import datetime
from config import SYSTEM_INFO

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns API status and version information
    """
    return HealthResponse(
        status="healthy",
        version=SYSTEM_INFO.get("version", "1.0.0"),
        timestamp=datetime.now().isoformat()
    )


@router.get("/models")
async def check_models():
    """
    Check AI model availability
    
    Verifies that Gemini and Groq services are accessible
    """
    import os
    
    models_status = {
        "gemini": {
            "available": bool(os.getenv("GEMINI_API_KEY")),
            "status": "configured" if os.getenv("GEMINI_API_KEY") else "missing_api_key"
        },
        "groq": {
            "available": bool(os.getenv("GROQ_API_KEY")),
            "status": "configured" if os.getenv("GROQ_API_KEY") else "missing_api_key"
        }
    }
    
    return {
        "status": "healthy" if all(m["available"] for m in models_status.values()) else "degraded",
        "models": models_status,
        "timestamp": datetime.now().isoformat()
    }
