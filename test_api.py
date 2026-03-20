"""
Test script to verify API is working
"""
import requests
import json

# Test 1: Health Check
print("=" * 70)
print("TEST 1: Health Check")
print("=" * 70)

response = requests.get("http://127.0.0.1:8000/api/health")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test 2: Analyze with sample data
print("=" * 70)
print("TEST 2: Upload Analysis (will fail without actual image)")
print("=" * 70)

patient_data = {
    "name": "Test Patient",
    "age": 45,
    "gender": "Male",
    "height_cm": 175.0,
    "weight_kg": 80.0,
    "profession": "Engineer"
}

mri_metadata = {
    "study_type": "Brain MRI",
    "sequence_type": "T2",
    "imaging_plane": "Axial"
}

# Note: This will fail without an actual image file
# Just showing the correct format
print("Patient Data JSON:")
print(json.dumps(patient_data, indent=2))
print()
print("MRI Metadata JSON:")
print(json.dumps(mri_metadata, indent=2))
print()
print("To upload, use these JSONs in the Swagger UI at:")
print("http://127.0.0.1:8000/docs")
