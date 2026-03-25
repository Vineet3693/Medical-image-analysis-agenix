"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         MIA APPLICATION                                      ║
║              Medical Image Analysis Workflow Integration                     ║
║                                                                              ║
║  This application orchestrates the complete MIA workflow by integrating      ║
║  all node modules into a seamless pipeline for medical image analysis.      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Application: MIA (Medical Image Analysis)
Description: Main application file that integrates all workflow nodes:
             1. Vision Analysis (Gemini 2.5 Flash)
             2. Cross Validation (Gemini 2.5 Flash)
             3. Report & Safety Analysis (Grok)
             4. PDF Generation

Author: MIA Team - Agenix AI
Created: 2026-01-07
Version: 2.0.0
"""

import os
import sys
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import all node modules
from nodes.mia_vision_analysis_node import vision_analysis_node
from nodes.mia_cross_validation_node import cross_validation_node
from nodes.mia_report_safety_node import report_safety_node
from nodes.mia_pdf_generation_node_new import pdf_generation_node

# Import utilities
from utils.logger import logger, log_workflow_step
from utils.patient_loader import PatientDataLoader
from config import OUTPUT_CONFIG


class MIAWorkflow:
    """
    MIA Workflow Orchestrator
    
    This class manages the complete medical image analysis workflow,
    coordinating the execution of all nodes in the correct sequence.
    
    Workflow Steps:
    1. User Input & Validation
    2. Vision Analysis (Gemini 2.5 Flash)
    3. Cross Validation (Gemini 2.5 Flash)
    4. Report & Safety Analysis (Grok)
    5. PDF Generation
    """
    
    def __init__(self):
        """Initialize the MIA Workflow."""
        self.workflow_name = "MIA Medical Image Analysis"
        self.version = "2.0.0"
        logger.info(f"Initializing {self.workflow_name} v{self.version}")
    
    def create_initial_state(self, patient_info: Dict[str, Any] = None,
                            mri_metadata: Dict[str, Any] = None,
                            mri_image_path: str = None,
                            report_type: str = "long") -> Dict[str, Any]:
        """
        Create initial workflow state.
        
        Args:
            patient_info: Patient information dictionary
            mri_metadata: MRI metadata dictionary
            mri_image_path: Path to MRI image
            
        Returns:
            Initial state dictionary
        """
        report_id = f"MIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        state = {
            "report_id": report_id,
            "patient_info": patient_info or {},
            "mri_metadata": mri_metadata or {},
            "mri_image_path": mri_image_path or "",
            "vision_analysis": {},
            "cross_validation": {},
            "report_content": {},
            "safety_analysis": {},
            "pdf_path": "",
            "report_type": report_type,  # None = will be chosen interactively; 'short' or 'long'
            "current_step": "initialization",
            "errors": []
        }
        
        logger.info(f"Created initial state for report: {report_id}")
        return state
    
    def collect_user_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect user input for the workflow.
        Supports automatic loading from patient JSON files.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with user input
        """
        log_workflow_step(state["report_id"], "user_input", "Collecting user input")
        
        # If data not provided, collect interactively
        if not state.get("mri_image_path") or not state.get("patient_info"):
            if sys.stdin.isatty():
                print("\n" + "=" * 80)
                print("MIA - MEDICAL IMAGE ANALYSIS SYSTEM")
                print("=" * 80)
                print(f"\nReport ID: {state['report_id']}")

                # ── STEP 1: Medical image path ─────────────────────────────────
                print("\n🔍 STEP 1: PROVIDE MEDICAL IMAGE\n")
                if not state.get("mri_image_path"):
                    print("📸 Medical Image:")
                    mri_path = input("   Enter image path (or press Enter for default): ").strip()
                    if not mri_path:
                        mri_path = "data/sample_mri/sample_brain.jpg"
                    state["mri_image_path"] = mri_path
                    print(f"   ✓ Image: {mri_path}\n")

                # ── STEP 2: Choose report format ───────────────────────────────
                if not state.get("report_type"):
                    print("\n" + "─" * 80)
                    print("📄 STEP 2: CHOOSE REPORT FORMAT\n")
                    print("   1. Short Report  —  compact 3-page summary")
                    print("      • Page 1: Cover + Patient Info + Clinical Impression")
                    print("      • Page 2: Findings Table + Medical Image")
                    print("      • Page 3: Full-size Medical Image")
                    print()
                    print("   2. Long Report   —  full comprehensive report (11 pages)")
                    print("      • Complete analysis, safety review & recommendations")
                    print()
                    report_choice = input("   Select format (1 = Short, 2 = Long, Enter = Short): ").strip()
                    if report_choice == "2":
                        state["report_type"] = "long"
                        print("   ✓ Report format: LONG (full report)\n")
                    else:
                        state["report_type"] = "short"
                        print("   ✓ Report format: SHORT (3 pages)\n")

                # ── STEP 3: Patient data ───────────────────────────────────────
                if not state.get("patient_info"):
                    print("\n" + "─" * 80)
                    print("👤 STEP 3: PATIENT DATA (JSON File)\n")
                    print("📁 Available patient files:")
                    
                    patient_loader = PatientDataLoader()
                    available_patients = patient_loader.list_available_patients()
                    
                    if available_patients:
                        for idx, patient_file in enumerate(available_patients, 1):
                            summary = patient_loader.get_patient_summary(patient_file)
                            print(f"   {idx}. {os.path.basename(patient_file)} - {summary}")
                        
                        print(f"\n   Or enter custom JSON file path")
                        patient_input = input("   Select patient (number or path): ").strip()
                        
                        if patient_input.isdigit():
                            idx = int(patient_input) - 1
                            if 0 <= idx < len(available_patients):
                                patient_file = available_patients[idx]
                            else:
                                print("   ⚠️ Invalid selection, using first patient")
                                patient_file = available_patients[0]
                        else:
                            patient_file = patient_input if patient_input else available_patients[0]
                        
                        try:
                            patient_data = patient_loader.load_patient_data(patient_file)
                            state["patient_info"] = patient_data["patient_info"]
                            state["mri_metadata"] = patient_data["mri_metadata"]
                            
                            print(f"\n   ✓ Loaded: {state['patient_info']['name']}")
                            print(f"   ✓ Study:  {state['mri_metadata']['study_type']}")
                            print(f"   ✓ Image:  {state['mri_image_path']}")
                            
                        except Exception as e:
                            print(f"\n   ❌ Error loading patient file: {e}")
                            state.setdefault("errors", []).append(f"Failed to load patient data: {str(e)}")
                            return state
                    else:
                        print("   ❌ No patient files found in data/patients/")
                        state.setdefault("errors", []).append("No patient files available")
                        return state

                print("\n" + "=" * 80)
                print("✅ Input collection complete — starting analysis...")
                print("=" * 80 + "\n")
            else:
                # Non-interactive mode: use defaults if data not already in state
                if not state.get("mri_image_path"):
                    state["mri_image_path"] = "data/sample_mri/sample_brain.jpg"
                
                if not state.get("patient_info"):
                    state["patient_info"] = {
                        "name": "John Doe",
                        "age": 45,
                        "gender": "Male",
                        "height_cm": 175.0,
                        "weight_kg": 80.0,
                        "bmi": 26.1,
                        "profession": "Engineer"
                    }
                
                if not state.get("mri_metadata"):
                    state["mri_metadata"] = {
                        "study_type": "Brain MRI",
                        "sequence_type": "T2",
                        "imaging_plane": "Axial"
                    }

                # Default to long report in non-interactive mode
                if not state.get("report_type"):
                    state["report_type"] = "long"

                logger.info("Non-interactive mode: using default values")
        
        return state
    
    def execute_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete MIA workflow.
        
        Args:
            state: Initial workflow state
            
        Returns:
            Final state with all results
        """
        report_id = state.get("report_id", "UNKNOWN")
        
        logger.info("=" * 80)
        logger.info(f"STARTING MIA WORKFLOW - {report_id}")
        logger.info("=" * 80)
        
        try:
            # Node 1: Vision Analysis
            logger.info("\n" + "=" * 80)
            logger.info("NODE 1: VISION ANALYSIS (Gemini 2.5 Flash)")
            logger.info("=" * 80)
            
            state = vision_analysis_node(state)
            
            if state.get("errors"):
                logger.error(f"Vision analysis failed with {len(state['errors'])} errors")
                return state
            
            logger.info("✓ Vision Analysis completed successfully\n")
            
            # Node 2: Cross Validation
            logger.info("=" * 80)
            logger.info("NODE 2: CROSS VALIDATION (Gemini 2.5 Flash)")
            logger.info("=" * 80)
            
            state = cross_validation_node(state)
            
            if state.get("errors"):
                logger.error(f"Cross validation failed with {len(state['errors'])} errors")
                return state
            
            logger.info("✓ Cross Validation completed successfully\n")
            
            # Node 3: Report & Safety Analysis
            logger.info("=" * 80)
            logger.info("NODE 3: REPORT & SAFETY ANALYSIS (Grok)")
            logger.info("=" * 80)
            
            state = report_safety_node(state)
            
            if state.get("errors"):
                logger.error(f"Report & safety analysis failed with {len(state['errors'])} errors")
                return state
            
            logger.info("✓ Report & Safety Analysis completed successfully\n")
            
            # Node 4: PDF Generation
            logger.info("=" * 80)
            logger.info("NODE 4: PDF GENERATION")
            logger.info("=" * 80)
            
            state = pdf_generation_node(state)
            
            if state.get("errors"):
                logger.error(f"PDF generation failed with {len(state['errors'])} errors")
                return state
            
            logger.info("✓ PDF Generation completed successfully\n")
            
            # Workflow completed
            logger.info("=" * 80)
            logger.info("MIA WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            
            log_workflow_step(report_id, "workflow_complete", 
                            f"All nodes completed successfully. PDF: {state.get('pdf_path', 'N/A')}", 
                            "SUCCESS")
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            logger.exception(e)
            state.setdefault("errors", []).append(f"Workflow error: {str(e)}")
        
        return state
    
    def print_summary(self, state: Dict[str, Any]):
        """
        Print workflow execution summary.
        
        Args:
            state: Final workflow state
        """
        print("\n" + "=" * 80)
        print("WORKFLOW EXECUTION SUMMARY")
        print("=" * 80)
        
        print(f"\n📋 Report ID: {state.get('report_id', 'N/A')}")
        print(f"👤 Patient: {state.get('patient_info', {}).get('name', 'N/A')}")
        print(f"🏥 Study: {state.get('mri_metadata', {}).get('study_type', 'N/A')}")
        
        # Image Classification
        if "image_classification" in state:
            ic = state["image_classification"]
            print(f"\n🔍 Image Classification:")
            print(f"   • Type: {ic.get('image_type', 'Unknown')}")
            print(f"   • Sub-Type: {ic.get('sub_type', 'N/A')}")
            print(f"   • Confidence: {ic.get('confidence', 0):.2%}")
            print(f"   • Region: {ic.get('anatomical_region', 'N/A')}")
        
        # Check for errors
        if state.get("errors"):
            print(f"\n❌ ERRORS ({len(state['errors'])}):")
            for error in state["errors"]:
                print(f"   • {error}")
        else:
            print("\n✅ Status: SUCCESS")
            
            # Vision Analysis
            if "vision_analysis" in state:
                va = state["vision_analysis"]
                print(f"\n🔍 Vision Analysis:")
                print(f"   • Findings: {len(va.get('findings', []))}")
                print(f"   • Measurements: {len(va.get('measurements', {}))}") 
                print(f"   • Confidence: {va.get('confidence_score', 0):.2%}")
            
            # Cross Validation
            if "cross_validation" in state:
                cv = state["cross_validation"]
                print(f"\n✓ Cross Validation:")
                print(f"   • Status: {cv.get('validation_status', 'N/A')}")
                print(f"   • Verified Findings: {len(cv.get('verified_findings', []))}")
                print(f"   • Discrepancies: {len(cv.get('discrepancies', []))}")
                
                # Groq Validation Results
                if "groq_validation" in cv:
                    gv = cv["groq_validation"]
                    if "groq_validation_summary" in gv:
                        gv_summary = gv["groq_validation_summary"]
                        print(f"\n🤖 Groq Cross-Validation:")
                        print(f"   • Consensus Score: {gv_summary.get('consensus_score', 0):.2%}")
                        print(f"   • Agreements: {gv_summary.get('agreements', 0)}")
                        print(f"   • Disagreements: {gv_summary.get('disagreements', 0)}")
                        print(f"   • Overall Confidence: {cv.get('confidence_score', 0):.2%}")
            
            # Safety Analysis
            if "safety_analysis" in state:
                sa = state["safety_analysis"]
                print(f"\n🛡️ Safety Analysis:")
                print(f"   • Safety Score: {sa.get('safety_score', 0):.1f}/100")
                print(f"   • Urgency Level: {sa.get('urgency_level', 'N/A')}")
                print(f"   • Critical Findings: {len(sa.get('critical_findings', []))}")
            
            # PDF Report
            if "pdf_path" in state and state["pdf_path"]:
                print(f"\n📄 PDF Report:")
                print(f"   • Path: {state['pdf_path']}")
                if os.path.exists(state["pdf_path"]):
                    file_size = os.path.getsize(state["pdf_path"])
                    print(f"   • Size: {file_size / 1024:.2f} KB")
                    print(f"   • Status: ✓ Generated")
                else:
                    print(f"   • Status: ⚠️ File not found")
        
        print("\n" + "=" * 80 + "\n")
    
    def run(self, patient_info: Dict[str, Any] = None,
            mri_metadata: Dict[str, Any] = None,
            mri_image_path: str = None,
            report_type: str = None) -> Dict[str, Any]:
        """
        Run the complete MIA workflow.
        
        Args:
            patient_info: Optional patient information
            mri_metadata: Optional MRI metadata
            mri_image_path: Optional MRI image path
            
        Returns:
            Final workflow state
        """
        # Create initial state
        state = self.create_initial_state(patient_info, mri_metadata, mri_image_path, report_type)
        
        # Collect user input if needed
        state = self.collect_user_input(state)
        
        # Execute workflow
        state = self.execute_workflow(state)
        
        # Print summary
        self.print_summary(state)
        
        return state


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main entry point for the MIA application.
    """
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "MIA - MEDICAL IMAGE ANALYSIS SYSTEM".center(78) + "║")
    print("║" + "Powered by Gemini 2.5 Flash & Grok".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    # Create workflow instance
    workflow = MIAWorkflow()
    
    # Run workflow (will collect input interactively if needed)
    final_state = workflow.run()
    
    # Return final state for programmatic access
    return final_state


if __name__ == "__main__":
    """
    Execute the MIA workflow when run as a script.
    """
    try:
        final_state = main()
        
        # Exit with appropriate code
        if final_state.get("errors"):
            sys.exit(1)  # Error
        else:
            sys.exit(0)  # Success
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Workflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        logger.exception(e)
        sys.exit(1)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

"""
Example 1: Run with interactive input
--------------------------------------
python miaapp.py


Example 2: Run programmatically with custom data
-------------------------------------------------
from miaapp import MIAWorkflow

workflow = MIAWorkflow()
result = workflow.run(
    patient_info={
        "name": "Jane Smith",
        "age": 35,
        "gender": "Female",
        "height_cm": 165.0,
        "weight_kg": 60.0,
        "bmi": 22.0,
        "profession": "Teacher"
    },
    mri_metadata={
        "study_type": "Brain MRI",
        "sequence_type": "T1",
        "imaging_plane": "Sagittal"
    },
    mri_image_path="path/to/mri/image.jpg"
)

print(f"PDF Report: {result['pdf_path']}")


Example 3: Access individual nodes
-----------------------------------
from nodes.mia_vision_analysis_node import vision_analysis_node
from nodes.mia_cross_validation_node import cross_validation_node

state = {"patient_info": {...}, "mri_image_path": "..."}
state = vision_analysis_node(state)
state = cross_validation_node(state)
"""
