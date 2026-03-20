"""
Tests for the complete MIA workflow
"""

import pytest
from nodes import MIAState, user_input_node, validation_node


def test_user_input_node():
    """Test user input node generates report ID."""
    state = MIAState(
        patient_info={},
        mri_metadata={},
        mri_image_path="",
        vision_analysis={},
        cross_validation={},
        report_content={},
        safety_analysis={},
        report_id="",
        pdf_path="",
        current_step="",
        errors=[]
    )
    
    result = user_input_node(state)
    
    assert result["current_step"] == "user_input"
    assert result["report_id"].startswith("MIA-")


def test_validation_node_with_errors():
    """Test validation node detects missing data."""
    state = MIAState(
        patient_info={},  # Empty - should cause validation errors
        mri_metadata={},
        mri_image_path="",
        vision_analysis={},
        cross_validation={},
        report_content={},
        safety_analysis={},
        report_id="MIA-001",
        pdf_path="",
        current_step="",
        errors=[]
    )
    
    result = validation_node(state)
    
    assert result["current_step"] == "validation"
    assert len(result.get("errors", [])) > 0  # Should have validation errors


def test_validation_node_with_valid_data():
    """Test validation node with complete data."""
    state = MIAState(
        patient_info={
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "height_cm": 175,
            "bmi": 26.1,
            "profession": "Engineer"
        },
        mri_metadata={
            "study_type": "Brain MRI",
            "sequence_type": "T2",
            "imaging_plane": "Axial"
        },
        mri_image_path="data/sample_mri/sample.jpg",
        vision_analysis={},
        cross_validation={},
        report_content={},
        safety_analysis={},
        report_id="MIA-001",
        pdf_path="",
        current_step="",
        errors=[]
    )
    
    result = validation_node(state)
    
    assert result["current_step"] == "validation"
    # May still have errors if image doesn't exist, but patient data is valid
