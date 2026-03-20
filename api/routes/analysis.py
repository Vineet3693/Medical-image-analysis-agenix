"""
Analysis API Routes
Main endpoint for MRI image analysis
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from api.schemas.requests import AnalysisRequest
from api.schemas.responses import (
    AnalysisStartResponse, 
    ReportResponse, 
    ReportListResponse,
    ReportListItem,
    StatusResponse,
    FindingResponse
)
from pathlib import Path
from datetime import datetime
import json
import logging
import shutil
from typing import Dict, Any

from miaapp import MIAWorkflow
from models.patient_data_schema import MIAReport

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Analysis"])

# In-memory storage for workflow states (in production, use Redis or database)
workflow_states: Dict[str, Dict[str, Any]] = {}


def save_uploaded_file(upload_file: UploadFile, report_id: str) -> str:
    """Save uploaded MRI image to disk"""
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(upload_file.filename).suffix
    filename = f"{report_id}_mri{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return str(file_path)


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculate BMI from height and weight"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def run_workflow_background(report_id: str, image_path: str, patient_data: dict, mri_metadata: dict):
    """Run MIA workflow in background"""
    try:
        logger.info(f"Starting background workflow for report: {report_id}")
        
        # Update status
        workflow_states[report_id]["status"] = "processing"
        workflow_states[report_id]["current_step"] = "initializing"
        
        # Create workflow instance
        workflow = MIAWorkflow()
        
        # Execute workflow
        final_state = workflow.run(
            patient_info=patient_data,
            mri_metadata=mri_metadata,
            mri_image_path=image_path
        )
        
        # Update state with results
        workflow_states[report_id]["status"] = "completed" if not final_state.get("errors") else "failed"
        workflow_states[report_id]["current_step"] = "completed"
        workflow_states[report_id]["result"] = final_state
        workflow_states[report_id]["pdf_path"] = final_state.get("pdf_path", "")
        workflow_states[report_id]["errors"] = final_state.get("errors", [])
        
        logger.info(f"Workflow completed for report: {report_id}")
        
    except Exception as e:
        logger.error(f"Workflow failed for report {report_id}: {str(e)}")
        workflow_states[report_id]["status"] = "failed"
        workflow_states[report_id]["errors"] = [str(e)]


@router.post("/analyze", response_model=AnalysisStartResponse)
async def analyze_mri(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(..., description="MRI image file (JPEG, PNG, DICOM)"),
    patient_data: str = Form(..., description="Patient information as JSON string"),
    mri_metadata: str = Form(..., description="MRI metadata as JSON string"),
    medical_report: UploadFile = File(None, description="Optional: Patient's medical report/history document (PDF, TXT, DOCX)")
):
    """
    Analyze MRI image with patient data
    
    Upload an MRI image along with patient information and MRI metadata.
    Optionally upload a medical report document for additional context.
    The analysis workflow will run in the background.
    
    **Parameters:**
    - **image**: MRI image file (required)
    - **patient_data**: JSON string with patient information (required)
    - **mri_metadata**: JSON string with MRI study metadata (required)
    - **medical_report**: Optional medical report document (PDF, TXT, DOCX)
    
    **Returns:**
    - Report ID for tracking the analysis
    """
    try:
        # Parse JSON data
        patient_info = json.loads(patient_data)
        mri_meta = json.loads(mri_metadata)
        
        # Generate report ID
        report_id = f"MIA-R{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate BMI if not provided
        if "bmi" not in patient_info or not patient_info["bmi"]:
            patient_info["bmi"] = calculate_bmi(
                patient_info["height_cm"],
                patient_info["weight_kg"]
            )
        
        # Add patient_id if not provided
        if "patient_id" not in patient_info or not patient_info["patient_id"]:
            patient_info["patient_id"] = report_id
        
        # Save uploaded image
        image_path = save_uploaded_file(image, report_id)
        
        # Save medical report if provided
        medical_report_path = None
        if medical_report and medical_report.filename:
            medical_report_path = save_uploaded_file(medical_report, f"{report_id}_medical_report")
            logger.info(f"Medical report uploaded: {medical_report_path}")
            # Add to patient info for workflow
            patient_info["medical_history_file"] = medical_report_path
        
        # Initialize workflow state
        workflow_states[report_id] = {
            "report_id": report_id,
            "patient_name": patient_info["name"],
            "study_type": mri_meta.get("study_type", "Brain MRI"),
            "status": "queued",
            "current_step": "queued",
            "created_at": datetime.now().isoformat(),
            "image_path": image_path,
            "medical_report_path": medical_report_path,
            "errors": []
        }
        
        # Start workflow in background
        background_tasks.add_task(
            run_workflow_background,
            report_id,
            image_path,
            patient_info,
            mri_meta
        )
        
        return AnalysisStartResponse(
            report_id=report_id,
            status="processing",
            message="Analysis workflow started successfully. Use /api/reports/{report_id}/status to track progress.",
            patient_name=patient_info["name"]
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except Exception as e:
        logger.error(f"Analysis request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/reports/{report_id}/status", response_model=StatusResponse)
async def get_report_status(report_id: str):
    """
    Get analysis workflow status
    
    Check the current status and progress of an analysis workflow.
    """
    if report_id not in workflow_states:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    state = workflow_states[report_id]
    
    # Calculate progress percentage
    progress_map = {
        "queued": 0,
        "initializing": 10,
        "vision_analysis": 30,
        "cross_validation": 50,
        "report_generation": 70,
        "pdf_generation": 90,
        "completed": 100,
        "failed": 0
    }
    
    progress = progress_map.get(state.get("current_step", "queued"), 0)
    
    return StatusResponse(
        report_id=report_id,
        status=state["status"],
        current_step=state.get("current_step", "unknown"),
        progress_percentage=progress,
        errors=state.get("errors", [])
    )


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """
    Get complete analysis report
    
    Retrieve the full analysis report including findings, impression, and recommendations.
    """
    if report_id not in workflow_states:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    state = workflow_states[report_id]
    
    if state["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Report not ready. Current status: {state['status']}"
        )
    
    result = state.get("result", {})
    report_content = result.get("report_content", {})
    
    # Extract findings
    findings = []
    if "findings" in report_content:
        for idx, finding in enumerate(report_content["findings"], 1):
            findings.append(FindingResponse(
                finding_id=idx,
                location=finding.get("location", "Unknown"),
                description=finding.get("description", ""),
                severity=finding.get("severity", "UNKNOWN"),
                clinical_significance=finding.get("clinical_significance", "")
            ))
    
    return ReportResponse(
        report_id=report_id,
        patient_name=state["patient_name"],
        study_type=state["study_type"],
        generated_at=state["created_at"],
        status=state["status"],
        findings=findings,
        impression=report_content.get("impression", ""),
        recommendations=report_content.get("recommendations", ""),
        urgency=report_content.get("urgency", "ROUTINE"),
        pdf_path=state.get("pdf_path", "")
    )


@router.get("/reports/{report_id}/pdf")
async def download_pdf(report_id: str):
    """
    Download PDF report
    
    Download the generated PDF report file.
    """
    if report_id not in workflow_states:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    state = workflow_states[report_id]
    
    if state["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"PDF not ready. Current status: {state['status']}"
        )
    
    pdf_path = state.get("pdf_path", "")
    
    if not pdf_path or not Path(pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{report_id}.pdf"
    )


@router.get("/reports", response_model=ReportListResponse)
async def list_reports():
    """
    List all analysis reports
    
    Get a list of all generated reports with their basic information.
    """
    reports = []
    
    for report_id, state in workflow_states.items():
        reports.append(ReportListItem(
            report_id=report_id,
            patient_name=state["patient_name"],
            study_type=state["study_type"],
            generated_at=state["created_at"],
            status=state["status"],
            pdf_available=bool(state.get("pdf_path") and Path(state.get("pdf_path", "")).exists())
        ))
    
    # Sort by creation time (newest first)
    reports.sort(key=lambda x: x.generated_at, reverse=True)
    
    return ReportListResponse(
        total=len(reports),
        reports=reports
    )
