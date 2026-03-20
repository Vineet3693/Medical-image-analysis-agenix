"""
Automatic MIA Workflow
Processes MRI images with pre-configured patient profiles
"""

import logging
import json
import os
from pathlib import Path
from mia_langgraph import create_mia_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def load_patient_profiles():
    """Load patient profiles from JSON file"""
    profiles_path = Path("data/patient_profiles.json")
    if profiles_path.exists():
        with open(profiles_path, 'r') as f:
            return json.load(f)
    return []


def select_patient():
    """Let user select a patient profile"""
    profiles = load_patient_profiles()
    
    if not profiles:
        logger.error("No patient profiles found!")
        return None
    
    print("\n" + "="*60)
    print("Available Patient Profiles")
    print("="*60)
    
    for i, patient in enumerate(profiles, 1):
        print(f"\n{i}. {patient['name']}")
        print(f"   Age: {patient['age']}, Gender: {patient['gender']}")
        print(f"   Study: {patient['study_type']}")
        print(f"   Indication: {patient['clinical_indication']}")
    
    print("\n" + "="*60)
    
    while True:
        try:
            choice = input(f"\nSelect patient (1-{len(profiles)}) or 0 to enter custom: ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return None  # Custom patient
            elif 1 <= choice_num <= len(profiles):
                return profiles[choice_num - 1]
            else:
                print(f"Please enter a number between 0 and {len(profiles)}")
        except ValueError:
            print("Please enter a valid number")


def main():
    """Run automatic MIA workflow"""
    
    print("\n" + "="*60)
    print("MIA - Medical Image Analysis System")
    print("Automatic Processing Mode")
    print("="*60)
    
    # Get MRI image path
    mri_path = input("\nEnter MRI image path: ").strip()
    
    if not mri_path:
        print("Error: MRI image path is required!")
        return
    
    if not os.path.exists(mri_path):
        print(f"Error: File not found: {mri_path}")
        return
    
    # Select patient
    patient = select_patient()
    
    if patient is None:
        print("\nEntering custom patient data...")
        # Fall back to interactive mode
        from run_interactive import main as interactive_main
        interactive_main()
        return
    
    print(f"\n✓ Selected: {patient['name']}")
    print(f"✓ MRI Image: {mri_path}")
    print("\nStarting automatic analysis...\n")
    
    # Create workflow
    app = create_mia_workflow()
    
    # Prepare state with selected patient
    initial_state = {
        "patient_info": {
            "name": patient["name"],
            "age": patient["age"],
            "gender": patient["gender"],
            "height_cm": patient["height_cm"],
            "weight_kg": patient["weight_kg"],
            "bmi": patient["bmi"],
            "profession": patient["profession"]
        },
        "mri_metadata": {
            "study_type": patient["study_type"],
            "sequence_type": patient["sequence_type"],
            "imaging_plane": patient["imaging_plane"]
        },
        "mri_image_path": mri_path,
        "vision_analysis": {},
        "cross_validation": {},
        "report_content": {},
        "safety_analysis": {},
        "report_id": "",
        "pdf_path": "",
        "current_step": "",
        "errors": []
    }
    
    try:
        # Execute workflow
        result = app.invoke(initial_state)
        
        # Display results
        print("\n" + "="*60)
        print("WORKFLOW COMPLETED")
        print("="*60)
        print(f"Patient: {patient['name']}")
        print(f"Report ID: {result.get('report_id')}")
        print(f"Current Step: {result.get('current_step')}")
        print(f"PDF Path: {result.get('pdf_path')}")
        
        if result.get("errors"):
            print(f"\n⚠️ Errors encountered:")
            for error in result["errors"]:
                print(f"  - {error}")
        else:
            print("\n✅ Analysis completed successfully!")
        
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user.")
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
