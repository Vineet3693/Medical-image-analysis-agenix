"""
Test Script for MIA Enhanced Features
Tests automatic image classification and Groq cross-validation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from miaapp import MIAWorkflow

def test_enhanced_workflow():
    """
    Test the enhanced MIA workflow with:
    1. Automatic image type classification
    2. Groq cross-validation
    """
    
    print("\n" + "=" * 80)
    print("TESTING ENHANCED MIA WORKFLOW")
    print("=" * 80)
    print("\nFeatures being tested:")
    print("✓ Automatic medical image type classification (Gemini)")
    print("✓ Dual-AI cross-validation (Gemini + Groq)")
    print("✓ Comparison matrix generation")
    print("✓ Consensus confidence scoring")
    print("\n" + "=" * 80 + "\n")
    
    # Create workflow instance
    workflow = MIAWorkflow()
    
    # Test data
    test_patient_info = {
        "name": "Test Patient",
        "age": 45,
        "gender": "Male",
        "height_cm": 175.0,
        "weight_kg": 80.0,
        "bmi": 26.1,
        "profession": "Engineer"
    }
    
    test_mri_metadata = {
        "study_type": "Brain MRI",
        "sequence_type": "T2",
        "imaging_plane": "Axial"
    }
    
    # Use sample image from data directory
    test_image_path = "data/sample_mri/sample.jpg"
    
    print(f"Test Image: {test_image_path}")
    print(f"Patient: {test_patient_info['name']}, {test_patient_info['age']} years old")
    print(f"Study: {test_mri_metadata['study_type']}")
    print("\n" + "=" * 80 + "\n")
    
    # Run workflow
    print("Starting workflow execution...\n")
    final_state = workflow.run(
        patient_info=test_patient_info,
        mri_metadata=test_mri_metadata,
        mri_image_path=test_image_path
    )
    
    # Detailed results
    print("\n" + "=" * 80)
    print("DETAILED TEST RESULTS")
    print("=" * 80)
    
    if final_state.get("errors"):
        print("\n❌ TEST FAILED - Errors detected:")
        for error in final_state["errors"]:
            print(f"   • {error}")
        return False
    
    # Image Classification Results
    if "image_classification" in final_state:
        ic = final_state["image_classification"]
        print("\n📸 IMAGE CLASSIFICATION RESULTS:")
        print(f"   • Detected Type: {ic.get('image_type', 'Unknown')}")
        print(f"   • Sub-Type: {ic.get('sub_type', 'N/A')}")
        print(f"   • Confidence: {ic.get('confidence', 0):.2%}")
        print(f"   • Anatomical Region: {ic.get('anatomical_region', 'N/A')}")
        print(f"   • Imaging Plane: {ic.get('imaging_plane', 'N/A')}")
        print(f"   • Characteristics: {len(ic.get('characteristics', []))} detected")
        
        if ic.get('confidence', 0) >= 0.85:
            print("   ✅ High confidence classification")
        elif ic.get('confidence', 0) >= 0.70:
            print("   ⚠️ Moderate confidence classification")
        else:
            print("   ❌ Low confidence classification")
    
    # Cross-Validation Results
    if "cross_validation" in final_state:
        cv = final_state["cross_validation"]
        print("\n🔍 CROSS-VALIDATION RESULTS:")
        print(f"   • Validation Status: {cv.get('validation_status', 'N/A')}")
        print(f"   • Verified Findings: {len(cv.get('verified_findings', []))}")
        print(f"   • Discrepancies: {len(cv.get('discrepancies', []))}")
        
        # Groq Validation
        if "groq_validation" in cv:
            gv = cv["groq_validation"]
            if "groq_validation_summary" in gv:
                gv_summary = gv["groq_validation_summary"]
                print("\n🤖 GROQ CROSS-VALIDATION:")
                print(f"   • Total Findings Reviewed: {gv_summary.get('total_findings_reviewed', 0)}")
                print(f"   • Agreements: {gv_summary.get('agreements', 0)}")
                print(f"   • Partial Agreements: {gv_summary.get('partial_agreements', 0)}")
                print(f"   • Disagreements: {gv_summary.get('disagreements', 0)}")
                print(f"   • Consensus Score: {gv_summary.get('consensus_score', 0):.2%}")
                
                consensus = gv_summary.get('consensus_score', 0)
                if consensus >= 0.85:
                    print("   ✅ High consensus between Gemini and Groq")
                elif consensus >= 0.70:
                    print("   ⚠️ Moderate consensus between Gemini and Groq")
                else:
                    print("   ❌ Low consensus - manual review recommended")
                
                # Comparison Matrix
                if "comparison_matrix" in gv:
                    matrix = gv["comparison_matrix"]
                    print(f"\n   📊 Comparison Matrix: {len(matrix)} findings compared")
                    for item in matrix[:3]:  # Show first 3
                        print(f"      • Finding {item.get('finding_id')}: {item.get('agreement_level')} "
                              f"(confidence: {item.get('confidence', 0):.2%})")
        
        print(f"\n   • Overall Confidence: {cv.get('confidence_score', 0):.2%}")
    
    # PDF Report
    if "pdf_path" in final_state and final_state["pdf_path"]:
        print(f"\n📄 PDF REPORT:")
        print(f"   • Path: {final_state['pdf_path']}")
        
        import os
        if os.path.exists(final_state["pdf_path"]):
            file_size = os.path.getsize(final_state["pdf_path"])
            print(f"   • Size: {file_size / 1024:.2f} KB")
            print("   ✅ Report generated successfully")
        else:
            print("   ❌ Report file not found")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETED SUCCESSFULLY")
    print("=" * 80 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_enhanced_workflow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
