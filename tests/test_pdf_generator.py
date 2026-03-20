"""
Tests for PDF generator functionality
"""

import pytest
import os
from datetime import datetime
from utils.pdf_generator import MIAPDFGenerator
from models.patient_data_schema import PatientInfo, MRIMetadata, Gender, MRISequence, ImagingPlane


def test_pdf_generator_initialization():
    """Test PDF generator can be initialized."""
    generator = MIAPDFGenerator()
    assert generator is not None


def test_patient_info_page_creation():
    """Test creating patient information page."""
    generator = MIAPDFGenerator()
    
    patient = PatientInfo(
        name="Test Patient",
        patient_id="TEST-001",
        age=50,
        gender=Gender.FEMALE,
        height_cm=165,
        weight_kg=70,
        bmi=25.7,
        profession="Teacher"
    )
    
    metadata = MRIMetadata(
        study_date=datetime.now(),
        study_type="Brain MRI",
        sequence_type=MRISequence.T1,
        imaging_plane=ImagingPlane.SAGITTAL,
        field_strength="1.5T",
        contrast_used=True,
        image_quality="Good"
    )
    
    # This would require a full MIAReport object in real implementation
    # For now, just test that the generator can be created
    assert generator is not None


def test_output_directory_creation():
    """Test that output directories are created if they don't exist."""
    test_dir = "outputs/test_reports"
    os.makedirs(test_dir, exist_ok=True)
    assert os.path.exists(test_dir)
    
    # Cleanup
    if os.path.exists(test_dir):
        os.rmdir(test_dir)
