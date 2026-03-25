"""
MIA API - Pydantic Request Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PatientInfoRequest(BaseModel):
    """Patient information for analysis request"""
    name: str = Field(..., description="Patient full name")
    patient_id: Optional[str] = Field(None, description="Patient ID (optional, will be auto-generated)")
    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    gender: str = Field(..., description="Patient gender (Male/Female/Other)")
    height_cm: float = Field(..., gt=0, description="Height in centimeters")
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")
    bmi: Optional[float] = Field(None, description="BMI (will be auto-calculated if not provided)")
    profession: str = Field("Unknown", description="Patient profession")
    medical_history: Optional[str] = Field(None, description="Relevant medical history")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "age": 45,
                "gender": "Male",
                "height_cm": 175.0,
                "weight_kg": 80.0,
                "profession": "Engineer",
                "medical_history": "No significant history"
            }
        }


class MRIMetadataRequest(BaseModel):
    """MRI study metadata"""
    study_type: str = Field("Brain MRI", description="Type of MRI study")
    sequence_type: str = Field("T2", description="MRI sequence type (T1/T2/FLAIR/etc)")
    imaging_plane: str = Field("Axial", description="Imaging plane (Axial/Sagittal/Coronal)")
    study_date: Optional[str] = Field(None, description="Study date (YYYY-MM-DD)")
    clinical_indication: Optional[str] = Field(None, description="Clinical indication for imaging")
    
    class Config:
        json_schema_extra = {
            "example": {
                "study_type": "Brain MRI",
                "sequence_type": "T2",
                "imaging_plane": "Axial",
                "clinical_indication": "Persistent headaches"
            }
        }


class AnalysisRequest(BaseModel):
    """Complete analysis request with patient and MRI metadata"""
    patient_info: PatientInfoRequest
    mri_metadata: MRIMetadataRequest
    report_type: Optional[str] = Field(
        "long",
        description="Report format: 'short' (3-page summary) or 'long' (full 11-page report)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_info": {
                    "name": "John Doe",
                    "age": 45,
                    "gender": "Male",
                    "height_cm": 175.0,
                    "weight_kg": 80.0,
                    "profession": "Engineer"
                },
                "mri_metadata": {
                    "study_type": "Brain MRI",
                    "sequence_type": "T2",
                    "imaging_plane": "Axial"
                },
                "report_type": "long"
            }
        }
