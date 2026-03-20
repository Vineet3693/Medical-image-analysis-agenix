"""
Tests for patient_data_schema.py models
"""

import pytest
from datetime import datetime
from models.patient_data_schema import (
    PatientInfo, MRIMetadata, Finding, DifferentialDiagnosis,
    Recommendations, Gender, UrgencyLevel, Severity, MRISequence, ImagingPlane
)


def test_patient_info_creation():
    """Test creating a valid PatientInfo object."""
    patient = PatientInfo(
        name="John Doe",
        patient_id="MIA-001",
        age=45,
        gender=Gender.MALE,
        height_cm=175,
        weight_kg=80,
        bmi=26.1,
        profession="Engineer"
    )
    
    assert patient.name == "John Doe"
    assert patient.age == 45
    assert patient.gender == Gender.MALE
    assert patient.bmi == 26.1


def test_mri_metadata_creation():
    """Test creating MRI metadata."""
    metadata = MRIMetadata(
        study_date=datetime.now(),
        study_type="Brain MRI",
        sequence_type=MRISequence.T2,
        imaging_plane=ImagingPlane.AXIAL,
        field_strength="3T",
        contrast_used=False,
        image_quality="Excellent"
    )
    
    assert metadata.study_type == "Brain MRI"
    assert metadata.sequence_type == MRISequence.T2
    assert metadata.imaging_plane == ImagingPlane.AXIAL


def test_finding_creation():
    """Test creating a Finding object."""
    finding = Finding(
        finding_id="F001",
        location="Frontal lobe",
        description="Small lesion detected",
        severity=Severity.MODERATE,
        measurements={"size_mm": 5.2}
    )
    
    assert finding.finding_id == "F001"
    assert finding.severity == Severity.MODERATE
    assert finding.measurements["size_mm"] == 5.2


def test_recommendations_creation():
    """Test creating Recommendations."""
    recommendations = Recommendations(
        urgency_level=UrgencyLevel.ROUTINE,
        immediate_actions=[],
        follow_up_imaging="Routine follow-up in 6 months",
        specialist_referrals=[],
        patient_counseling=["Continue regular monitoring"]
    )
    
    assert recommendations.urgency_level == UrgencyLevel.ROUTINE
    assert len(recommendations.patient_counseling) == 1
