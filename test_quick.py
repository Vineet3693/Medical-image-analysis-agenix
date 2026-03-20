"""
Quick Test Script for MIA with Pre-loaded Patient Data
"""

from miaapp import MIAWorkflow
from utils import load_patient_data

# Load patient data from JSON
patient_data = load_patient_data("e:/MIA/data/patients/patient_001_robert_johnson.json")

# Create workflow
workflow = MIAWorkflow()

# Run with pre-loaded data
final_state = workflow.run(
    patient_info=patient_data["patient_info"],
    mri_metadata=patient_data["mri_metadata"],
    mri_image_path="data/input/hand.jpg"
)

# Print summary
print("\n" + "=" * 80)
print("TEST COMPLETED!")
print("=" * 80)

if final_state.get("errors"):
    print("\n❌ ERRORS:")
    for error in final_state["errors"]:
        print(f"   • {error}")
else:
    print("\n✅ SUCCESS!")
    
    # Show results
    if "image_classification" in final_state:
        ic = final_state["image_classification"]
        print(f"\n📸 Image Type: {ic.get('image_type')} ({ic.get('confidence', 0):.2%})")
    
    if "cross_validation" in final_state:
        cv = final_state["cross_validation"]
        if "groq_validation" in cv:
            gv_summary = cv["groq_validation"].get("groq_validation_summary", {})
            print(f"🤖 Consensus Score: {gv_summary.get('consensus_score', 0):.2%}")
    
    if "pdf_path" in final_state:
        print(f"\n📄 PDF: {final_state['pdf_path']}")

print("\n" + "=" * 80)
