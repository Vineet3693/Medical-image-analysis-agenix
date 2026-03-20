"""
Simple test script to demonstrate MIA workflow
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mia_langgraph import create_mia_workflow
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def main():
    print("\n" + "="*70)
    print("MIA WORKFLOW DEMONSTRATION")
    print("="*70)
    
    # Create workflow
    app = create_mia_workflow()
    
    # Test data - Robert Johnson with Brain MRI
    initial_state = {
        "patient_info": {
            "name": "Robert Johnson",
            "age": 45,
            "gender": "Male",
            "height_cm": 178,
            "weight_kg": 85,
            "bmi": 26.8,
            "profession": "Software Engineer"
        },
        "mri_metadata": {
            "study_type": "Brain MRI",
            "sequence_type": "T2",
            "imaging_plane": "Axial"
        },
        "mri_image_path": "data/sample_mri/sample_brain.jpg",
        "vision_analysis": {},
        "cross_validation": {},
        "report_content": {},
        "safety_analysis": {},
        "report_id": "",
        "pdf_path": "",
        "current_step": "",
        "errors": []
    }
    
    print("\n📋 Patient: Robert Johnson (45M)")
    print("📊 Study: Brain MRI (T2 Axial)")
    print("🖼️  Image: data/sample_mri/sample_brain.jpg")
    print("\n" + "="*70)
    print("EXECUTING WORKFLOW...")
    print("="*70 + "\n")
    
    try:
        # Execute workflow
        result = app.invoke(initial_state)
        
        # Display results
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETED")
        print("="*70)
        print(f"Patient: {result['patient_info']['name']}")
        print(f"Report ID: {result.get('report_id')}")
        print(f"Final Step: {result.get('current_step')}")
        print(f"PDF Path: {result.get('pdf_path')}")
        
        if result.get("errors"):
            print(f"\n⚠️  Errors Encountered ({len(result['errors'])}):")
            for i, error in enumerate(result["errors"], 1):
                print(f"  {i}. {error}")
        else:
            print("\n✅ No errors - All nodes executed successfully!")
        
        # Show what was processed
        print("\n📊 Processing Summary:")
        print(f"  - Vision Analysis: {'✅ Completed' if result.get('vision_analysis') else '❌ Skipped'}")
        print(f"  - Cross-Validation: {'✅ Completed' if result.get('cross_validation') else '❌ Skipped'}")
        print(f"  - Report Generation: {'✅ Completed' if result.get('report_content') else '❌ Skipped'}")
        print(f"  - Safety Analysis: {'✅ Completed' if result.get('safety_analysis') else '❌ Skipped'}")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
