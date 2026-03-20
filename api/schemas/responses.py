"""
MIA API - Pydantic Response Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-01-23T12:00:00"
            }
        }


class AnalysisStartResponse(BaseModel):
    """Response when analysis is initiated"""
    report_id: str = Field(..., description="Unique report ID for tracking")
    status: str = Field(..., description="Initial status")
    message: str = Field(..., description="Status message")
    patient_name: str = Field(..., description="Patient name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "MIA-R001",
                "status": "processing",
                "message": "Analysis workflow started successfully",
                "patient_name": "John Doe"
            }
        }


class FindingResponse(BaseModel):
    """Individual finding in the report"""
    finding_id: int
    location: str
    description: str
    severity: str
    clinical_significance: str


class ReportResponse(BaseModel):
    """Complete analysis report response"""
    report_id: str
    patient_name: str
    study_type: str
    generated_at: str
    status: str
    findings: List[FindingResponse] = []
    impression: Optional[str] = None
    recommendations: Optional[str] = None
    urgency: Optional[str] = None
    pdf_path: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "MIA-R001",
                "patient_name": "John Doe",
                "study_type": "Brain MRI",
                "generated_at": "2026-01-23T12:00:00",
                "status": "completed",
                "findings": [],
                "impression": "No significant abnormalities detected",
                "recommendations": "Routine follow-up recommended",
                "urgency": "ROUTINE"
            }
        }


class ReportListItem(BaseModel):
    """Report list item for listing all reports"""
    report_id: str
    patient_name: str
    study_type: str
    generated_at: str
    status: str
    pdf_available: bool


class ReportListResponse(BaseModel):
    """List of all reports"""
    total: int
    reports: List[ReportListItem]


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid patient data provided",
                "detail": "Age must be between 0 and 150"
            }
        }


class StatusResponse(BaseModel):
    """Workflow status response"""
    report_id: str
    status: str
    current_step: str
    progress_percentage: int
    errors: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "MIA-R001",
                "status": "processing",
                "current_step": "vision_analysis",
                "progress_percentage": 40,
                "errors": []
            }
        }
