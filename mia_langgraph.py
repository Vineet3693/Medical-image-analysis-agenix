"""
MIA LangGraph Workflow Engine
Orchestrates the medical image analysis process using consolidated nodes.
"""

import logging
from langgraph.graph import StateGraph, END
from datetime import datetime

# Import nodes and state definition
from nodes import (
    MIAState,
    user_input_node,
    validation_node,
    vision_node,
    cross_validation_node,
    report_node,
    safety_node,
    pdf_node
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mia_workflow() -> StateGraph:
    """Create the MIA LangGraph workflow using consolidated nodes."""
    
    workflow = StateGraph(MIAState)
    
    # Add nodes from consolidated nodes.py
    workflow.add_node("user_input", user_input_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("vision", vision_node)
    workflow.add_node("cross_validation", cross_validation_node)
    workflow.add_node("report", report_node)
    workflow.add_node("safety", safety_node)
    workflow.add_node("pdf", pdf_node)
    
    # Define edges and transitions
    workflow.set_entry_point("user_input")
    workflow.add_edge("user_input", "validation")
    workflow.add_edge("validation", "vision")
    workflow.add_edge("vision", "cross_validation")
    workflow.add_edge("cross_validation", "report")
    workflow.add_edge("report", "safety")
    workflow.add_edge("safety", "pdf")
    workflow.add_edge("pdf", END)
    
    return workflow.compile()

def run_workflow_example():
    """Execute a test run of the compiled workflow."""
    logger.info("=" * 60)
    logger.info("MIA Workflow Runner")
    logger.info("=" * 60)
    
    app = create_mia_workflow()
    
    # Minimal initialization - user_input_node will collect data interactively
    initial_state = {
        "patient_info": {},
        "mri_metadata": {},
        "image_metadata": {},
        "medical_image_path": "",
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
        result = app.invoke(initial_state)
        logger.info(f"Workflow Status: {result.get('current_step')}")
        logger.info(f"Report ID: {result.get('report_id')}")
        logger.info(f"PDF Path: {result.get('pdf_path')}")
        
        if result.get("errors"):
            logger.warning(f"Workflow Errors: {result['errors']}")
            
    except Exception as e:
        logger.error(f"Execution failed: {e}")

if __name__ == "__main__":
    run_workflow_example()
