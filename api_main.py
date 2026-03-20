"""
MIA FastAPI Application
Medical Image Analysis REST API

This FastAPI application provides REST endpoints for the MIA Medical Image Analysis system.
It allows clients to upload MRI images with patient data and receive analysis reports.

Author: MIA Team - Agenix AI
Version: 1.0.0
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pathlib import Path
import logging

# Import routers
from api.routes import health, analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MIA - Medical Image Analysis API",
    description="""
    **MIA (Medical Image Analysis)** REST API provides automated analysis of medical images using AI.
    
    ## Features
    
    * **AI-Powered Analysis**: Uses Gemini 2.5 Flash and Groq for accurate medical image analysis
    * **Comprehensive Reports**: Generates detailed PDF reports with findings and recommendations
    * **Cross-Validation**: Dual AI model validation for increased accuracy
    * **Safety Analysis**: Automated urgency assessment and safety recommendations
    
    ## Workflow
    
    1. Upload MRI image with patient data via `/api/analyze`
    2. Track analysis progress via `/api/reports/{report_id}/status`
    3. Retrieve complete report via `/api/reports/{report_id}`
    4. Download PDF report via `/api/reports/{report_id}/pdf`
    
    ## Authentication
    
    Currently no authentication required (development mode).
    """,
    version="1.0.0",
    contact={
        "name": "MIA Team - Agenix AI",
        "email": "support@agenix.ai"
    },
    license_info={
        "name": "Proprietary",
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(analysis.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("=" * 70)
    logger.info("MIA FastAPI Application Starting")
    logger.info("=" * 70)
    
    # Create necessary directories
    directories = [
        "data/uploads",
        "data/outputs",
        "data/outputs/reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory ready: {directory}")
    
    logger.info("✓ MIA API is ready to accept requests")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("MIA FastAPI Application Shutting Down")


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")


@app.get("/api", include_in_schema=False)
async def api_root():
    """API root endpoint"""
    return {
        "message": "MIA - Medical Image Analysis API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/api/health",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "reports": "GET /api/reports",
            "report_detail": "GET /api/reports/{report_id}",
            "report_status": "GET /api/reports/{report_id}/status",
            "download_pdf": "GET /api/reports/{report_id}/pdf"
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 70)
    print("🏥 MIA - Medical Image Analysis API")
    print("=" * 70)
    print("\nStarting server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("📍 Health Check: http://localhost:8000/api/health")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(
        "api_main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
