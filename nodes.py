"""
MIA LangGraph Nodes implementation.
Contains all logical steps for the medical image analysis workflow.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, TypedDict
from langgraph.graph import END

from services import get_gemini_service, get_groq_service
from utils import PromptLoader, generate_mia_report
from utils.validators import validate_patient_info, validate_image_path, validate_mri_metadata
from utils.logger import logger, log_workflow_step, log_patient_processing, log_error_with_context
from config import OUTPUT_CONFIG

import sys


class MIAState(dict):
    """Mutable state object for MIA workflow that behaves like a dict but is initializable."""
    def __init__(
        self,
        patient_info: Dict[str, Any] = None,
        mri_metadata: Dict[str, Any] = None,
        mri_image_path: str = "",
        vision_analysis: Dict[str, Any] = None,
        cross_validation: Dict[str, Any] = None,
        report_content: Dict[str, Any] = None,
        safety_analysis: Dict[str, Any] = None,
        report_id: str = "",
        pdf_path: str = "",
        current_step: str = "",
        errors: List[str] = None,
    ):
        super().__init__()
        self["patient_info"] = patient_info or {}
        self["mri_metadata"] = mri_metadata or {}
        self["mri_image_path"] = mri_image_path or ""
        self["vision_analysis"] = vision_analysis or {}
        self["cross_validation"] = cross_validation or {}
        self["report_content"] = report_content or {}
        self["safety_analysis"] = safety_analysis or {}
        self["report_id"] = report_id or ""
        self["pdf_path"] = pdf_path or ""
        self["current_step"] = current_step or ""
        self["errors"] = errors or []

def user_input_node(state: MIAState) -> MIAState:
    """Collect and validate initial report context."""
    report_id = state.get("report_id") or f"MIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    log_workflow_step(report_id, "user_input", "Starting user input collection")
    state["current_step"] = "user_input"
    
    # Generate report ID if not already set
    if not state.get("report_id"):
        state["report_id"] = f"MIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Interactive input if data not provided
    if not state.get("mri_image_path"):
        # If running interactively, prompt the user; else use sensible defaults for tests/automation
        if sys.stdin.isatty():
            print("\n" + "="*60)
            print("MIA - Medical Image Analysis System")
            print("="*60)
            print("\nPlease provide the following information:\n")
            
            # Get MRI image path
            mri_path = input("Enter MRI image path (or press Enter for default): ").strip()
            if not mri_path:
                mri_path = "data/sample_mri/sample.jpg"
            state["mri_image_path"] = mri_path
            
            # Get patient information
            print("\n--- Patient Information ---")
            patient_name = input("Patient Name (default: John Doe): ").strip() or "John Doe"
            patient_age = input("Patient Age (default: 45): ").strip() or "45"
            patient_gender = input("Patient Gender (Male/Female, default: Male): ").strip() or "Male"
            patient_height = input("Height in cm (default: 175): ").strip() or "175"
            patient_weight = input("Weight in kg (default: 80): ").strip() or "80"
            patient_profession = input("Profession (default: Engineer): ").strip() or "Engineer"
            
            # Calculate BMI
            height_m = float(patient_height) / 100
            bmi = float(patient_weight) / (height_m ** 2)
            
            state["patient_info"] = {
                "name": patient_name,
                "age": int(patient_age),
                "gender": patient_gender,
                "height_cm": float(patient_height),
                "weight_kg": float(patient_weight),
                "bmi": round(bmi, 1),
                "profession": patient_profession
            }
            
            # Get MRI metadata
            print("\n--- MRI Study Information ---")
            study_type = input("Study Type (default: Brain MRI): ").strip() or "Brain MRI"
            sequence_type = input("Sequence Type (default: T2): ").strip() or "T2"
            imaging_plane = input("Imaging Plane (default: Axial): ").strip() or "Axial"
            
            state["mri_metadata"] = {
                "study_type": study_type,
                "sequence_type": sequence_type,
                "imaging_plane": imaging_plane
            }
            
            print("\n" + "="*60)
            print(f"Report ID: {state['report_id']}")
            print("="*60 + "\n")
        else:
            # Non-interactive mode (tests, CI): set sensible defaults without prompting
            state["mri_image_path"] = "data/sample_mri/sample.jpg"
            state["patient_info"] = {
                "name": "John Doe",
                "age": 45,
                "gender": "Male",
                "height_cm": 175.0,
                "weight_kg": 80.0,
                "bmi": 26.1,
                "profession": "Engineer"
            }
            state["mri_metadata"] = {
                "study_type": "Brain MRI",
                "sequence_type": "T2",
                "imaging_plane": "Axial"
            }
            log_workflow_step(state["report_id"], "user_input", "Non-interactive mode: defaults applied")
    
    return state

def validation_node(state: MIAState) -> MIAState:
    """Validate all input data before processing."""
    log_workflow_step(state.get("report_id", "UNKNOWN"), "validation", "Validating input data")
    state["current_step"] = "validation"
    
    errors = []
    errors.extend(validate_patient_info(state.get("patient_info", {})))
    errors.extend(validate_mri_metadata(state.get("mri_metadata", {})))
    errors.extend(validate_image_path(state.get("mri_image_path", "")))
    
    if errors:
        state.setdefault("errors", []).extend(errors)
        log_workflow_step(state.get("report_id", "UNKNOWN"), "validation", f"Validation failed: {len(errors)} errors", "ERROR")
        for error in errors:
            logger.error(f"Validation error: {error}")
        
    return state

def vision_node(state: MIAState) -> MIAState:
    """Analyze MRI image using Gemini 2.5 Flash Vision capabilities."""
    report_id = state.get("report_id", "UNKNOWN")
    log_workflow_step(report_id, "vision_analysis", "Starting Gemini vision analysis")
    state["current_step"] = "vision_analysis"
    
    if state.get("errors"): return state

    try:
        gemini = get_gemini_service()
        prompt_loader = PromptLoader()
        prompt = prompt_loader.get_vision_analysis_prompt(state["patient_info"])
        
        vision_results = gemini.perform_vision_analysis(
            image_path=state["mri_image_path"],
            prompt=prompt
        )
        
        state["vision_analysis"] = vision_results
        log_workflow_step(report_id, "vision_analysis", "Vision analysis completed successfully")
    except Exception as e:
        log_error_with_context(e, {"report_id": report_id, "step": "vision_analysis"})
        state.setdefault("errors", []).append(f"Vision analysis error: {str(e)}")
    
    return state

def cross_validation_node(state: MIAState) -> MIAState:
    """Cross-validate vision results for anatomical and clinical consistency."""
    logger.info("Node: Cross-Validation (Gemini)")
    state["current_step"] = "cross_validation"
    
    if state.get("errors"): return state

    try:
        gemini = get_gemini_service()
        prompt_loader = PromptLoader()
        prompt = prompt_loader.get_cross_validation_prompt(
            vision_results=state["vision_analysis"],
            patient_info=state["patient_info"]
        )
        
        validation_results = gemini.perform_cross_validation(
            image_path=state["mri_image_path"],
            prompt=prompt
        )
        
        state["cross_validation"] = validation_results
        logger.info("Cross-validation completed successfully")
    except Exception as e:
        logger.error(f"Cross-validation failed: {e}")
        state.setdefault("errors", []).append(f"Cross-validation error: {str(e)}")
    
    return state

def report_node(state: MIAState) -> MIAState:
    """Generate professional medical report using Groq."""
    logger.info("Node: Report Generation (Groq)")
    state["current_step"] = "report_generation"
    
    if state.get("errors"): return state

    try:
        groq = get_groq_service()
        prompt_loader = PromptLoader()
        prompt = prompt_loader.get_report_generation_prompt(
            vision_results=state["vision_analysis"],
            validation_results=state["cross_validation"],
            patient_info=state["patient_info"],
            mri_metadata=state["mri_metadata"]
        )
        
        report_data = groq.generate_report(prompt)
        state["report_content"] = report_data
        logger.info("Medical report generated by Groq")
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        state.setdefault("errors", []).append(f"Report generation error: {str(e)}")
    
    return state

def safety_node(state: MIAState) -> MIAState:
    """Perform clinical safety check and critical finding verification."""
    logger.info("Node: Safety Analysis (Groq)")
    state["current_step"] = "safety_analysis"
    
    if state.get("errors"): return state

    try:
        groq = get_groq_service()
        prompt_loader = PromptLoader()
        prompt = prompt_loader.get_safety_analysis_prompt(
            vision_results=state["vision_analysis"],
            validation_results=state["cross_validation"],
            report_content=state["report_content"],
            patient_info=state["patient_info"]
        )
        
        safety_results = groq.perform_safety_analysis(prompt)
        state["safety_analysis"] = safety_results
        logger.info("Safety analysis completed")
    except Exception as e:
        logger.error(f"Safety analysis failed: {e}")
        state.setdefault("errors", []).append(f"Safety analysis error: {str(e)}")
    
    return state

def pdf_node(state: MIAState) -> MIAState:
    """Compile final report into a professional PDF format."""
    logger.info("Node: PDF Generation")
    state["current_step"] = "pdf_generation"
    
    if state.get("errors"): 
        logger.warning("Skipping PDF generation due to previous errors")
        return state

    try:
        from models.patient_data_schema import (
            PatientInfo, MRIMetadata, Finding, MIAReport,
            Severity, UrgencyLevel  # Fixed: Use Severity and UrgencyLevel
        )
        from datetime import datetime
        
        # Extract data from state
        patient_data = state.get("patient_info", {})
        mri_data = state.get("mri_metadata", {})
        vision_data = state.get("vision_analysis", {})
        validation_data = state.get("cross_validation", {})
        report_data = state.get("report_content", {})
        safety_data = state.get("safety_analysis", {})
        
        # Create PatientInfo model
        patient_info = PatientInfo(
            name=patient_data.get("name", "Unknown Patient"),
            age=patient_data.get("age", 0),
            gender=patient_data.get("gender", "Unknown"),
            patient_id=patient_data.get("patient_id", state.get("report_id", "UNKNOWN")),
            height_cm=patient_data.get("height_cm", 0),
            weight_kg=patient_data.get("weight_kg", 0),
            bmi=patient_data.get("bmi", 0.0),
            medical_history=patient_data.get("medical_history", "Not provided"),
            profession=patient_data.get("profession", "Not specified")
        )
        
        # Create MRIMetadata model
        mri_metadata = MRIMetadata(
            study_type=mri_data.get("study_type", "MRI Study"),
            study_date=datetime.now(),
            sequence_type=mri_data.get("sequence_type", "Unknown"),
            imaging_plane=mri_data.get("imaging_plane", "Unknown"),
            field_strength="1.5T",  # Default
            contrast_used=False,  # Default
            clinical_indication=patient_data.get("clinical_indication", "Medical imaging analysis")
        )
        
        # Extract findings from vision analysis
        findings = []
        if isinstance(vision_data, dict) and "findings" in vision_data:
            for idx, finding_data in enumerate(vision_data.get("findings", []), 1):
                if isinstance(finding_data, dict):
                    finding = Finding(
                        finding_id=idx,
                        location=finding_data.get("location", "Not specified"),
                        description=finding_data.get("description", "No description"),
                        severity=Severity.MODERATE,  # Fixed: Use Severity enum
                        measurements=finding_data.get("measurements", {}),
                        clinical_significance=finding_data.get("clinical_significance", "Under review")
                    )
                    findings.append(finding)
        
        # If no structured findings, create a general finding from report
        if not findings and report_data:
            general_finding = Finding(
                finding_id=1,
                location="General",
                description=str(report_data.get("raw_response", "Analysis completed"))[:500],
                severity=Severity.MILD,  # Fixed: Use Severity enum
                clinical_significance="Refer to detailed report"
            )
            findings.append(general_finding)
        
        # Create MIAReport model
        mia_report = MIAReport(
            report_id=state.get("report_id", f"MIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
            patient_info=patient_info,
            mri_metadata=mri_metadata,
            findings=findings,
            impression=str(report_data.get("raw_response", "Analysis completed"))[:1000] if report_data else "Report generated successfully",
            recommendations="Please consult with your healthcare provider for detailed interpretation.",
            urgency=UrgencyLevel.ROUTINE,  # Fixed: Use UrgencyLevel enum
            generated_at=datetime.now(),
            generated_by="MIA Team - Agenix AI",
            gemini_analysis=vision_data if isinstance(vision_data, dict) else {},
            gemini_validation=validation_data if isinstance(validation_data, dict) else {},
            groq_report=report_data if isinstance(report_data, dict) else {},
            groq_safety=safety_data if isinstance(safety_data, dict) else {}
        )
        
        # Generate PDF
        output_dir = OUTPUT_CONFIG['reports_dir']
        logger.info(f"Generating PDF report in: {output_dir}")
        
        pdf_path = generate_mia_report(mia_report, str(output_dir))
        
        state["pdf_path"] = pdf_path
        logger.info(f"PDF generated successfully: {pdf_path}")
        
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        logger.exception(e)
        state.setdefault("errors", []).append(f"PDF generation error: {str(e)}")
    
    return state

