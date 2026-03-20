"""
Interactive MIA Workflow Runner
Prompts user for MRI image and patient data
"""

import logging
from mia_langgraph import create_mia_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run interactive MIA workflow"""
    
    # Create workflow
    app = create_mia_workflow()
    
    # Start with empty state - user_input_node will collect data interactively
    initial_state = {
        "patient_info": {},
        "mri_metadata": {},
        "mri_image_path": "",
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
        print(f"Report ID: {result.get('report_id')}")
        print(f"Current Step: {result.get('current_step')}")
        print(f"PDF Path: {result.get('pdf_path')}")
        
        if result.get("errors"):
            print(f"\n⚠️ Errors encountered:")
            for error in result["errors"]:
                print(f"  - {error}")
        else:
            print("\n✅ Workflow completed successfully!")
        
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user.")
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
