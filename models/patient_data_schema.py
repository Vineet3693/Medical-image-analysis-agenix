"""
Patient Data Schema for MIA System
Defines Pydantic models for patient information, MRI metadata, and analysis results
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    """Gender enumeration"""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class UrgencyLevel(str, Enum):
    """Urgency classification for findings"""
    IMMEDIATE = "Immediate"
    URGENT = "Urgent"
    SEMI_URGENT = "Semi-urgent"
    ROUTINE = "Routine"


class Severity(str, Enum):
    """Severity classification"""
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"
    CRITICAL = "Critical"


class MRISequence(str, Enum):
    """MRI sequence types"""
    T1 = "T1"
    T2 = "T2"
    FLAIR = "FLAIR"
    DWI = "DWI"
    T1_CONTRAST = "T1 with Contrast"
    T2_FLAIR = "T2 FLAIR"
    SWI = "SWI"
    OTHER = "Other"


class ImagingPlane(str, Enum):
    """Imaging plane orientations"""
    AXIAL = "Axial"
    SAGITTAL = "Sagittal"
    CORONAL = "Coronal"
    OBLIQUE = "Oblique"


class PatientInfo(BaseModel):
    """Patient demographic information"""
    name: str = Field(..., description="Patient full name")
    patient_id: Optional[str] = Field(None, description="Unique patient identifier")
    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    gender: Gender = Field(..., description="Patient gender")
    height_cm: float = Field(..., gt=0, description="Patient height in centimeters")
    weight_kg: Optional[float] = Field(None, gt=0, description="Patient weight in kilograms")
    bmi: float = Field(..., gt=0, description="Body Mass Index")
    profession: str = Field(..., description="Patient occupation/profession")
    medical_history: Optional[str] = Field(None, description="Patient medical history")
    date_of_birth: Optional[datetime] = Field(None, description="Patient date of birth")
    
    @validator('bmi', pre=True, always=True)
    def calculate_bmi(cls, v, values):
        """Calculate BMI if not provided"""
        if v is None and 'height_cm' in values and 'weight_kg' in values:
            height_m = values['height_cm'] / 100
            return round(values['weight_kg'] / (height_m ** 2), 1)
        return v
    
    class Config:
        use_enum_values = True


class MRIMetadata(BaseModel):
    """MRI study metadata"""
    study_date: datetime = Field(..., description="Date of MRI study")
    study_type: str = Field(..., description="Type of MRI study (e.g., Brain, Spine)")
    sequence_type: MRISequence = Field(..., description="MRI sequence type")
    imaging_plane: ImagingPlane = Field(..., description="Imaging plane")
    field_strength: Optional[str] = Field(None, description="MRI field strength (e.g., 1.5T, 3T)")
    contrast_used: bool = Field(False, description="Whether contrast was administered")
    contrast_type: Optional[str] = Field(None, description="Type of contrast agent")
    slice_thickness_mm: Optional[float] = Field(None, description="Slice thickness in mm")
    image_quality: Optional[str] = Field(None, description="Overall image quality assessment")
    artifacts_present: bool = Field(False, description="Whether artifacts are present")
    artifact_description: Optional[str] = Field(None, description="Description of artifacts")
    clinical_indication: Optional[str] = Field(None, description="Clinical indication for the study")
    
    class Config:
        use_enum_values = True


class Measurement(BaseModel):
    """Measurement data for findings"""
    length_mm: Optional[float] = Field(None, description="Length in millimeters")
    width_mm: Optional[float] = Field(None, description="Width in millimeters")
    height_mm: Optional[float] = Field(None, description="Height in millimeters")
    volume_cm3: Optional[float] = Field(None, description="Volume in cubic centimeters")
    area_mm2: Optional[float] = Field(None, description="Area in square millimeters")


class Finding(BaseModel):
    """Individual finding from analysis"""
    finding_id: int = Field(..., description="Unique finding identifier")
    location: str = Field(..., description="Anatomical location")
    description: str = Field(..., description="Detailed description of finding")
    measurements: Optional[Measurement] = Field(None, description="Quantitative measurements")
    signal_characteristics: Optional[str] = Field(None, description="Signal intensity characteristics")
    severity: Severity = Field(..., description="Severity classification")
    clinical_significance: str = Field(..., description="Clinical significance")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    
    class Config:
        use_enum_values = True


class DifferentialDiagnosis(BaseModel):
    """Differential diagnosis entry"""
    condition: str = Field(..., description="Condition name")
    probability: str = Field(..., description="Probability (High/Medium/Low)")
    supporting_features: List[str] = Field(..., description="Supporting imaging features")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in diagnosis")


class Recommendations(BaseModel):
    """Clinical recommendations"""
    urgency_level: UrgencyLevel = Field(..., description="Urgency classification")
    timeframe: str = Field(..., description="Recommended timeframe for action")
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate actions needed")
    follow_up_imaging: Optional[str] = Field(None, description="Follow-up imaging recommendations")
    specialist_referrals: List[str] = Field(default_factory=list, description="Specialist referrals")
    additional_studies: List[str] = Field(default_factory=list, description="Additional diagnostic studies")
    patient_counseling: List[str] = Field(default_factory=list, description="Patient counseling points")
    
    class Config:
        use_enum_values = True


class VisionAnalysisResult(BaseModel):
    """Results from Gemini vision analysis"""
    image_quality: Dict[str, Any] = Field(..., description="Image quality assessment")
    anatomical_structures: Dict[str, Any] = Field(..., description="Identified anatomical structures")
    findings: List[Finding] = Field(default_factory=list, description="List of findings")
    differential_diagnosis: List[DifferentialDiagnosis] = Field(default_factory=list)
    recommendations: Recommendations = Field(..., description="Clinical recommendations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    limitations: List[str] = Field(default_factory=list, description="Analysis limitations")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


class CrossValidationResult(BaseModel):
    """Results from Gemini cross-validation"""
    validation_summary: Dict[str, Any] = Field(..., description="Validation summary")
    visual_verification: Dict[str, Any] = Field(..., description="Visual verification results")
    measurement_validation: Dict[str, Any] = Field(..., description="Measurement validation")
    anatomical_consistency: Dict[str, Any] = Field(..., description="Anatomical consistency check")
    clinical_plausibility: Dict[str, Any] = Field(..., description="Clinical plausibility assessment")
    final_recommendations: Dict[str, Any] = Field(..., description="Final recommendations")
    validator_confidence: float = Field(..., ge=0.0, le=1.0, description="Validator confidence")
    validation_timestamp: datetime = Field(default_factory=datetime.now)


class ReportContent(BaseModel):
    """Generated report content from Grok"""
    report_metadata: Dict[str, Any] = Field(..., description="Report metadata")
    page_1_patient_info: Dict[str, Any] = Field(..., description="Patient information page")
    page_2_imaging: Dict[str, Any] = Field(..., description="Imaging display page")
    page_3_analysis: Dict[str, Any] = Field(..., description="Analysis and findings")
    generation_timestamp: datetime = Field(default_factory=datetime.now)


class SafetyAnalysisResult(BaseModel):
    """Results from Grok safety analysis"""
    safety_analysis_summary: Dict[str, Any] = Field(..., description="Safety analysis summary")
    critical_findings_check: Dict[str, Any] = Field(..., description="Critical findings check")
    confidence_assessment: Dict[str, Any] = Field(..., description="Confidence assessment")
    consistency_validation: Dict[str, Any] = Field(..., description="Consistency validation")
    medical_appropriateness: Dict[str, Any] = Field(..., description="Medical appropriateness")
    patient_safety_assessment: Dict[str, Any] = Field(..., description="Patient safety assessment")
    quality_control: Dict[str, Any] = Field(..., description="Quality control checks")
    required_actions: List[Dict[str, Any]] = Field(default_factory=list)
    escalation_required: Dict[str, Any] = Field(..., description="Escalation requirements")
    final_disclaimer: Dict[str, Any] = Field(..., description="Final disclaimer text")
    safety_timestamp: datetime = Field(default_factory=datetime.now)


class MIAReport(BaseModel):
    """Complete MIA analysis report"""
    report_id: str = Field(..., description="Unique report identifier")
    patient_info: PatientInfo = Field(..., description="Patient information")
    mri_metadata: MRIMetadata = Field(..., description="MRI study metadata")
    findings: List[Finding] = Field(default_factory=list, description="List of findings")
    impression: str = Field(..., description="Overall impression")
    recommendations: str = Field(..., description="Clinical recommendations")
    urgency: UrgencyLevel = Field(..., description="Urgency level")
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = Field(default="MIA System", description="Report generator")
    
    # Raw analysis data from workflow
    gemini_analysis: Dict[str, Any] = Field(default_factory=dict, description="Gemini vision analysis raw data")
    gemini_validation: Dict[str, Any] = Field(default_factory=dict, description="Gemini cross-validation raw data")
    groq_report: Dict[str, Any] = Field(default_factory=dict, description="Groq report generation raw data")
    groq_safety: Dict[str, Any] = Field(default_factory=dict, description="Groq safety analysis raw data")
    
    mri_image_path: Optional[str] = Field(None, description="Path to MRI/medical image file")
    pdf_path: Optional[str] = Field(None, description="Path to generated PDF report")
    
    class Config:
        use_enum_values = True
