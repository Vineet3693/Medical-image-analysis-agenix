"""
Example usage of MIA System
Demonstrates how to use the complete workflow for MRI analysis
"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from models.patient_data_schema import (
    PatientInfo, MRIMetadata, MIAReport,
    Gender, MRISequence, ImagingPlane
)
from utils.pdf_generator import generate_mia_report
from config import OUTPUT_CONFIG

# Load environment variables
load_dotenv()


def create_sample_patient_info() -> PatientInfo:
    """Create sample patient information"""
    return PatientInfo(
        name="John Doe",
        patient_id="MIA-2026-001",
        age=45,
        gender=Gender.MALE,
        height_cm=175,
        weight_kg=80,
        bmi=26.1,
        profession="Software Engineer",
        date_of_birth=datetime(1981, 1, 15)
    )


def create_sample_mri_metadata() -> MRIMetadata:
    """Create sample MRI metadata"""
    return MRIMetadata(
        study_date=datetime.now(),
        study_type="Brain MRI",
        sequence_type=MRISequence.T2,
        imaging_plane=ImagingPlane.AXIAL,
        field_strength="3T",
        contrast_used=False,
        image_quality="Excellent",
        artifacts_present=False
    )


def main():
    """
    Main function to demonstrate MIA workflow
    
    Workflow:
    1. User Input - Collect patient data and MRI image
    2. Validation - Validate inputs
    3. Vision Analysis - Gemini analyzes MRI image
    4. Cross Validation - Gemini validates results
    5. Report Generation - Grok generates report
    6. Safety Analysis - Grok performs safety checks
    7. PDF Generation - Create final PDF report
    """
    
    print("=" * 60)
    print("MIA - Medical Image Analysis System")
    print("Dual-LLM Architecture: Gemini + Grok")
    print("=" * 60)
    print()
    
    # Step 1: Collect patient information
    print("Step 1: Creating patient information...")
    patient_info = create_sample_patient_info()
    print(f"  Patient: {patient_info.name}, Age: {patient_info.age}")
    print()
    
    # Step 2: Create MRI metadata
    print("Step 2: Creating MRI metadata...")
    mri_metadata = create_sample_mri_metadata()
    print(f"  Study Type: {mri_metadata.study_type}")
    print(f"  Sequence: {mri_metadata.sequence_type}")
    print()
    
    # Step 3: Specify MRI image path
    print("Step 3: Specifying MRI image...")
    # TODO: Replace with actual MRI image path
    mri_image_path = "path/to/your/mri_image.jpg"
    print(f"  Image Path: {mri_image_path}")
    print()
    
    # Step 4: Vision Analysis (Gemini)
    print("Step 4: Running Vision Analysis (Gemini 2.5 Flash)...")
    print("  [This would call Gemini API with vision analysis prompt]")
    print("  [Analyzing MRI image for findings, measurements, etc.]")
    # TODO: Implement actual Gemini vision analysis call
    vision_results = {
        "image_quality": {"overall_quality": "Excellent"},
        "anatomical_structures": {"primary_structures": ["Brain", "Ventricles"]},
        "findings": [],
        "differential_diagnosis": [],
        "recommendations": {
            "urgency_level": "Routine",
            "timeframe": "Within 1 month"
        },
        "confidence_score": 0.92,
        "limitations": []
    }
    print("  ✓ Vision analysis complete")
    print()
    
    # Step 5: Cross Validation (Gemini)
    print("Step 5: Running Cross Validation (Gemini 2.5 Flash)...")
    print("  [This would call Gemini API with cross-validation prompt]")
    print("  [Validating findings, measurements, and consistency]")
    # TODO: Implement actual Gemini cross-validation call
    validation_results = {
        "validation_summary": {
            "overall_agreement": "High",
            "confidence_in_original_analysis": 0.95,
            "validation_status": "Approved"
        },
        "visual_verification": {},
        "measurement_validation": {},
        "anatomical_consistency": {},
        "clinical_plausibility": {},
        "final_recommendations": {},
        "validator_confidence": 0.93
    }
    print("  ✓ Cross validation complete")
    print()
    
    # Step 6: Report Generation (Grok)
    print("Step 6: Generating Medical Report (Grok)...")
    print("  [This would call Grok API with report generation prompt]")
    print("  [Creating comprehensive medical report]")
    # TODO: Implement actual Grok report generation call
    report_content = {
        "report_metadata": {
            "report_id": "MIA-RPT-2026-001",
            "generation_date": datetime.now().isoformat()
        },
        "page_1_patient_info": {},
        "page_2_imaging": {},
        "page_3_analysis": {
            "technique": "MRI brain imaging performed with T2 sequence.",
            "image_quality": "Excellent image quality with no significant artifacts.",
            "anatomical_structures": "Normal brain anatomy visualized.",
            "findings": [],
            "impression": ["No acute intracranial abnormality identified."],
            "differential_diagnosis": [],
            "clinical_correlation": {
                "age_considerations": "Age-appropriate findings.",
                "profession_factors": "No occupation-specific concerns identified.",
                "bmi_considerations": "BMI within normal range."
            },
            "recommendations": {
                "urgency_level": "ROUTINE",
                "immediate_actions": [],
                "follow_up_imaging": "Routine follow-up as clinically indicated.",
                "specialist_referrals": [],
                "patient_counseling": ["Continue regular health monitoring."]
            },
            "quality_assurance": {
                "confidence_score": 0.92,
                "validation_status": "Approved"
            },
            "disclaimer": "This report is AI-generated and requires validation by a qualified radiologist."
        }
    }
    print("  ✓ Report generation complete")
    print()
    
    # Step 7: Safety Analysis (Grok)
    print("Step 7: Running Safety Analysis (Grok)...")
    print("  [This would call Grok API with safety analysis prompt]")
    print("  [Checking for critical findings, confidence, consistency]")
    # TODO: Implement actual Grok safety analysis call
    safety_results = {
        "safety_analysis_summary": {
            "overall_safety_status": "Safe",
            "approval_recommendation": "Approve",
            "safety_score": 0.95,
            "risk_level": "Low"
        },
        "critical_findings_check": {"critical_findings_present": False},
        "confidence_assessment": {},
        "consistency_validation": {},
        "medical_appropriateness": {},
        "patient_safety_assessment": {},
        "quality_control": {},
        "required_actions": [],
        "escalation_required": {"requires_escalation": False},
        "final_disclaimer": {
            "disclaimer_text": "This AI-generated report should be reviewed by a qualified medical professional."
        }
    }
    print("  ✓ Safety analysis complete")
    print()
    
    # Step 8: Create complete MIA report object
    print("Step 8: Creating complete MIA report...")
    # Note: In actual implementation, you would use the Pydantic models properly
    # This is a simplified example
    print("  [Assembling all components into MIAReport object]")
    print("  ✓ Report object created")
    print()
    
    # Step 9: Generate PDF
    print("Step 9: Generating PDF Report...")
    print("  [This would call PDF generator with complete report data]")
    print("  [Creating professional A4 PDF with patient details, images, and analysis]")
    # TODO: Implement actual PDF generation
    # output_path = generate_mia_report(mia_report, OUTPUT_CONFIG["reports_dir"])
    print("  ✓ PDF generation complete")
    print(f"  Output: {OUTPUT_CONFIG['reports_dir']}/MIA-2026-001_MIA-RPT-2026-001.pdf")
    print()
    
    print("=" * 60)
    print("MIA Analysis Complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  • Patient analyzed: John Doe (45 years old)")
    print("  • Study type: Brain MRI (T2 Axial)")
    print("  • Vision analysis: Gemini 2.5 Flash (confidence: 92%)")
    print("  • Cross-validation: Gemini 2.5 Flash (confidence: 93%)")
    print("  • Report generation: Grok")
    print("  • Safety analysis: Grok (safety score: 95%)")
    print("  • PDF report: Generated successfully")
    print()
    print("Next steps:")
    print("  1. Provide your logo file in assets/logo.png")
    print("  2. Configure API keys in .env file")
    print("  3. Integrate with actual LangGraph workflow")
    print("  4. Test with real MRI images")
    print()


if __name__ == "__main__":
    main()
