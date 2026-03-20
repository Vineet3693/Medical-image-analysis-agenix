"""
Patient Data Loader Utility
Loads patient information and MRI metadata from JSON files
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PatientDataLoader:
    """Utility to load patient data from JSON files"""
    
    def __init__(self, patients_dir: Optional[Path] = None):
        """
        Initialize PatientDataLoader
        
        Args:
            patients_dir: Directory containing patient JSON files
        """
        self.patients_dir = patients_dir or Path(__file__).parent.parent / "data" / "patients"
        logger.info(f"PatientDataLoader initialized with directory: {self.patients_dir}")
    
    def load_patient_data(self, patient_file_path: str) -> Dict[str, Any]:
        """
        Load patient data from JSON file
        
        Args:
            patient_file_path: Path to patient JSON file
            
        Returns:
            Dictionary containing patient_info and mri_metadata
        """
        try:
            # Handle both absolute and relative paths
            if not os.path.isabs(patient_file_path):
                patient_file_path = os.path.join(self.patients_dir, patient_file_path)
            
            logger.info(f"Loading patient data from: {patient_file_path}")
            
            if not os.path.exists(patient_file_path):
                raise FileNotFoundError(f"Patient file not found: {patient_file_path}")
            
            with open(patient_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract patient information
            patient_info = {
                "patient_id": data.get("patient_id", "UNKNOWN"),
                "name": data.get("name", "Unknown Patient"),
                "age": data.get("age", 0),
                "gender": data.get("gender", "Unknown"),
                "height_cm": float(data.get("height_cm", 0)),
                "weight_kg": float(data.get("weight_kg", 0)),
                "bmi": float(data.get("bmi", 0)),
                "profession": data.get("profession", "Unknown"),
                "medical_history": data.get("medical_history", ""),
                "clinical_indication": data.get("clinical_indication", ""),
                "date_of_birth": data.get("date_of_birth", ""),
                "referring_physician": data.get("referring_physician", ""),
                "contact_phone": data.get("contact_phone", ""),
                "emergency_contact": data.get("emergency_contact", "")
            }
            
            # Extract MRI metadata
            mri_metadata = {
                "study_type": data.get("study_type", "Unknown Study"),
                "sequence_type": data.get("sequence_type", "Unknown"),
                "imaging_plane": data.get("imaging_plane", "Unknown")
            }
            
            logger.info(f"Successfully loaded data for patient: {patient_info['name']}")
            logger.info(f"Study type: {mri_metadata['study_type']}")
            
            return {
                "patient_info": patient_info,
                "mri_metadata": mri_metadata
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in patient file: {e}")
            raise ValueError(f"Invalid JSON format in patient file: {e}")
        except Exception as e:
            logger.error(f"Error loading patient data: {e}")
            raise
    
    def list_available_patients(self) -> list:
        """
        List all available patient JSON files
        
        Returns:
            List of patient file paths
        """
        if not self.patients_dir.exists():
            logger.warning(f"Patients directory not found: {self.patients_dir}")
            return []
        
        patient_files = list(self.patients_dir.glob("patient_*.json"))
        logger.info(f"Found {len(patient_files)} patient files")
        
        return [str(f) for f in patient_files]
    
    def get_patient_summary(self, patient_file_path: str) -> str:
        """
        Get a brief summary of patient data
        
        Args:
            patient_file_path: Path to patient JSON file
            
        Returns:
            Summary string
        """
        try:
            data = self.load_patient_data(patient_file_path)
            patient_info = data["patient_info"]
            mri_metadata = data["mri_metadata"]
            
            summary = f"{patient_info['name']} ({patient_info['age']}y, {patient_info['gender']}) - {mri_metadata['study_type']}"
            return summary
        except Exception as e:
            return f"Error loading patient: {e}"


# Convenience function
def load_patient_data(patient_file_path: str) -> Dict[str, Any]:
    """
    Quick function to load patient data
    
    Args:
        patient_file_path: Path to patient JSON file
        
    Returns:
        Dictionary with patient_info and mri_metadata
    """
    loader = PatientDataLoader()
    return loader.load_patient_data(patient_file_path)
