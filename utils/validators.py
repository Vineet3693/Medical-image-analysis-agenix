"""
Input validation utilities for the MIA system.
"""

import os
from typing import Dict, Any, List

def validate_patient_info(info: Dict[str, Any]) -> List[str]:
    """Validate patient demographic information."""
    errors = []
    required = ["name", "age", "gender", "height_cm", "bmi", "profession"]
    for field in required:
        if field not in info:
            errors.append(f"Missing required patient field: {field}")
    return errors

def validate_image_path(path: str) -> List[str]:
    """Validate that the MRI image path exists and is a file."""
    if not path:
        return ["MRI image path is empty."]
    if not os.path.exists(path):
        return [f"MRI image path does not exist: {path}"]
    if not os.path.isfile(path):
        return [f"MRI image path is not a file: {path}"]
    return []

def validate_mri_metadata(metadata: Dict[str, Any]) -> List[str]:
    """Validate MRI study metadata."""
    errors = []
    required = ["study_type", "sequence_type", "imaging_plane"]
    for field in required:
        if field not in metadata:
            errors.append(f"Missing required MRI metadata field: {field}")
    return errors
