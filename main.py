"""
MIA - Medical Image Analysis System
Main Entry Point

This is the primary interface for running the complete MIA workflow.
It guides users through each step of the medical image analysis process.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mia_langgraph import create_mia_workflow
from utils.logger import logger, log_workflow_step, log_patient_processing
from models.patient_data_schema import PatientInfo, MRIMetadata


def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print("🏥 MIA - Medical Image Analysis System")
    print("   Powered by Gemini 2.5 Flash & Groq AI")
    print("="*70 + "\n")


def print_step_header(step_num: int, step_name: str):
    """Print step header"""
    print("\n" + "-"*70)
    print(f"📍 Step {step_num}: {step_name}")
    print("-"*70)


def get_medical_image_path() -> str:
    """
    Step 1: Get medical image path from user
    
    Returns:
        Path to medical image file
    """
    print_step_header(1, "Medical Image Selection")
    
    print("\nPlease provide the path to your medical image.")
    print("Supported formats: JPEG, PNG, DICOM")
    print("Supported modalities: MRI, X-Ray, CT, Ultrasound, PET, Mammography, etc.")
    print("\nExample: C:\\Images\\chest_xray.jpg")
    print("         data/sample_mri/sample_brain.jpg")
    
    while True:
        image_path = input("\n📁 Enter medical image path: ").strip()
        
        if not image_path:
            print("❌ Error: Image path cannot be empty!")
            continue
        
        # Remove quotes if present
        image_path = image_path.strip('"').strip("'")
        
        if os.path.exists(image_path):
            print(f"✅ Image found: {image_path}")
            return image_path
        else:
            print(f"❌ Error: File not found: {image_path}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                sys.exit(0)


def load_patient_profiles() -> list:
    """Load patient profiles from individual JSON files"""
    patients_dir = Path("data/patients")
    profiles = []
    
    if patients_dir.exists():
        # Load all patient JSON files
        for patient_file in sorted(patients_dir.glob("patient_*.json")):
            try:
                with open(patient_file, 'r') as f:
                    patient_data = json.load(f)
                    profiles.append(patient_data)
            except Exception as e:
                logger.warning(f"Failed to load {patient_file}: {e}")
    
    # Fallback to old combined file if no individual files found
    if not profiles:
        old_path = Path("data/patient_profiles.json")
        if old_path.exists():
            with open(old_path, 'r') as f:
                profiles = json.load(f)
    
    return profiles


def select_patient() -> dict:
    """
    Step 2: Select patient profile by providing file path
    
    Returns:
        Selected patient data dictionary
    """
    print_step_header(2, "Patient Profile Selection")
    
    print("\n📋 Patient Profile Options:\n")
    print("1. Provide path to patient JSON file")
    print("2. Enter custom patient data manually")
    
    print("\n💡 Example patient files:")
    print("   - data/patients/patient_001_robert_johnson.json")
    print("   - data/patients/patient_002_maria_garcia.json")
    print("   - data/patients/patient_003_david_chen.json")
    print("   - data/patients/patient_004_sarah_williams.json")
    print("   - data/patients/patient_005_james_thompson.json")
    
    while True:
        choice = input("\n📁 Enter patient file path (or 'custom' for manual entry): ").strip()
        
        if not choice:
            print("❌ Error: Please provide a file path or type 'custom'")
            continue
        
        # Remove quotes if present
        choice = choice.strip('"').strip("'")
        
        if choice.lower() == 'custom':
            return create_custom_patient()
        
        # Try to load the patient file
        patient_path = Path(choice)
        if patient_path.exists():
            try:
                with open(patient_path, 'r') as f:
                    patient_data = json.load(f)
                print(f"\n✅ Loaded: {patient_data.get('name', 'Unknown')}")
                print(f"   Study: {patient_data.get('study_type', 'N/A')}")
                return patient_data
            except json.JSONDecodeError as e:
                print(f"❌ Error: Invalid JSON file - {e}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return create_custom_patient()
            except Exception as e:
                print(f"❌ Error loading file: {e}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return create_custom_patient()
        else:
            print(f"❌ Error: File not found: {choice}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return create_custom_patient()


def create_custom_patient() -> dict:
    """Create custom patient data"""
    print("\n📝 Enter Custom Patient Data:\n")
    
    name = input("Patient Name: ").strip() or "John Doe"
    age = int(input("Age: ").strip() or "45")
    gender = input("Gender (Male/Female): ").strip() or "Male"
    height = float(input("Height (cm): ").strip() or "175")
    weight = float(input("Weight (kg): ").strip() or "80")
    profession = input("Profession: ").strip() or "Engineer"
    
    # Calculate BMI
    bmi = weight / ((height / 100) ** 2)
    
    print("\n📊 Study Information:\n")
    study_type = input("Study Type (e.g., Chest X-Ray, Brain MRI, Abdominal CT): ").strip() or "Brain MRI"
    sequence = input("Sequence/Technique (e.g., T2, PA, Axial): ").strip() or "T2"
    plane = input("Imaging Plane (e.g., Axial, Sagittal, AP): ").strip() or "Axial"
    
    return {
        "name": name,
        "age": age,
        "gender": gender,
        "height_cm": height,
        "weight_kg": weight,
        "bmi": round(bmi, 1),
        "profession": profession,
        "study_type": study_type,
        "sequence_type": sequence,
        "imaging_plane": plane
    }


def confirm_and_start(image_path: str, patient: dict) -> bool:
    """
    Step 3: Confirm details and start processing
    
    Args:
        image_path: Path to MRI image
        patient: Patient data dictionary
    
    Returns:
        True if user confirms, False otherwise
    """
    print_step_header(3, "Confirmation")
    
    print("\n📋 Analysis Summary:")
    print(f"\n👤 Patient: {patient['name']}")
    print(f"   Age: {patient['age']}, Gender: {patient['gender']}")
    print(f"   BMI: {patient['bmi']}, Profession: {patient['profession']}")
    print(f"\n🏥 Study: {patient['study_type']}")
    print(f"   Sequence: {patient['sequence_type']}")
    print(f"   Plane: {patient['imaging_plane']}")
    print(f"\n📁 Image: {image_path}")
    
    print("\n" + "="*70)
    confirm = input("\n✅ Start analysis? (y/n): ").strip().lower()
    return confirm == 'y'


def execute_workflow(image_path: str, patient: dict):
    """
    Step 4: Execute the complete MIA workflow
    
    Args:
        image_path: Path to MRI image
        patient: Patient data dictionary
    """
    print_step_header(4, "Workflow Execution")
    
    # Create workflow
    app = create_mia_workflow()
    
    # Prepare initial state using modality-agnostic key names
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
        "image_metadata": {
            "study_type": patient["study_type"],
            "sequence_type": patient["sequence_type"],
            "imaging_plane": patient["imaging_plane"]
        },
        "medical_image_path": image_path,
        "vision_analysis": {},
        "cross_validation": {},
        "report_content": {},
        "safety_analysis": {},
        "report_id": "",
        "pdf_path": "",
        "current_step": "",
        "errors": []
    }
    
    print("\n🚀 Starting workflow execution...\n")
    
    # Log patient processing
    log_patient_processing(patient["name"], patient.get("patient_id", "CUSTOM"), patient["study_type"])
    
    try:
        # Execute workflow
        print("⏳ Processing through all nodes...")
        print("   1️⃣  User Input")
        print("   2️⃣  Validation")
        print("   3️⃣  Vision Analysis (Gemini)")
        print("   4️⃣  Cross-Validation (Gemini)")
        print("   5️⃣  Report Generation (Groq)")
        print("   6️⃣  Safety Analysis (Groq)")
        print("   7️⃣  PDF Generation")
        print()
        
        result = app.invoke(initial_state)
        
        # Display results
        display_results(result, patient)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during workflow execution: {e}")
        logger.exception(e)
        sys.exit(1)


def display_results(result: dict, patient: dict):
    """
    Display workflow results
    
    Args:
        result: Workflow result state
        patient: Patient data
    """
    print("\n" + "="*70)
    print("📊 WORKFLOW RESULTS")
    print("="*70)
    
    print(f"\n👤 Patient: {patient['name']}")
    print(f"📋 Report ID: {result.get('report_id', 'N/A')}")
    print(f"📍 Final Step: {result.get('current_step', 'N/A')}")
    
    # Check for errors
    if result.get("errors"):
        print(f"\n⚠️  Errors Encountered ({len(result['errors'])}):")
        for i, error in enumerate(result["errors"], 1):
            print(f"   {i}. {error}")
    else:
        print("\n✅ No errors - Workflow completed successfully!")
    
    # Show processing summary
    print("\n📊 Processing Summary:")
    print(f"   Vision Analysis: {'✅ Completed' if result.get('vision_analysis') else '❌ Skipped/Failed'}")
    print(f"   Cross-Validation: {'✅ Completed' if result.get('cross_validation') else '❌ Skipped/Failed'}")
    print(f"   Report Generation: {'✅ Completed' if result.get('report_content') else '❌ Skipped/Failed'}")
    print(f"   Safety Analysis: {'✅ Completed' if result.get('safety_analysis') else '❌ Skipped/Failed'}")
    
    # PDF output
    if result.get('pdf_path'):
        print(f"\n📄 PDF Report: {result['pdf_path']}")
    else:
        print(f"\n📄 PDF Report: Not generated")
    
    # Log files
    print(f"\n📝 Logs: outputs/logs/")
    print(f"   - Main log: mia_{datetime.now().strftime('%Y%m%d')}.log")
    print(f"   - Errors: mia_errors_{datetime.now().strftime('%Y%m%d')}.log")
    print(f"   - Workflow: workflow_{datetime.now().strftime('%Y%m%d')}.log")
    
    print("\n" + "="*70)


def main():
    """Main application entry point"""
    try:
        # Print header
        print_header()
        
        # Step 1: Get medical image
        image_path = get_medical_image_path()
        
        # Step 2: Select patient
        patient = select_patient()
        
        # Step 3: Confirm and start
        if not confirm_and_start(image_path, patient):
            print("\n❌ Analysis cancelled by user.")
            return
        
        # Step 4: Execute workflow
        execute_workflow(image_path, patient)
        
        print("\n✅ MIA workflow completed!")
        print("Thank you for using MIA - Medical Image Analysis System\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Application terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
