# Patient Profile Files

This directory contains individual patient profile files in JSON format.

## Available Patients

### 1. Robert Johnson (MIA-P001)
**File**: `patient_001_robert_johnson.json`
- Age: 45, Male
- Study: Brain MRI (T2 Axial)
- Indication: Persistent headaches for 3 months
- Medical History: Hypertension, occasional migraines

### 2. Maria Garcia (MIA-P002)
**File**: `patient_002_maria_garcia.json`
- Age: 52, Female
- Study: Lumbar Spine MRI (T1/T2 Sagittal)
- Indication: Lower back pain radiating to left leg
- Medical History: Type 2 Diabetes, controlled with medication

### 3. David Chen (MIA-P003)
**File**: `patient_003_david_chen.json`
- Age: 38, Male
- Study: Cervical Spine MRI (T2 Axial)
- Indication: Neck pain following motor vehicle accident
- Medical History: No significant medical history

### 4. Sarah Williams (MIA-P004)
**File**: `patient_004_sarah_williams.json`
- Age: 61, Female
- Study: Knee MRI (T1 Coronal)
- Indication: Right knee pain and swelling
- Medical History: Osteoarthritis, previous knee surgery (2018)

### 5. James Thompson (MIA-P005)
**File**: `patient_005_james_thompson.json`
- Age: 29, Male
- Study: Shoulder MRI (T2 Coronal)
- Indication: Recurrent shoulder instability
- Medical History: Previous shoulder dislocation (2023)

## File Format

Each patient file contains:
- `patient_id`: Unique identifier
- `name`: Patient full name
- `age`: Age in years
- `gender`: Male/Female
- `height_cm`: Height in centimeters
- `weight_kg`: Weight in kilograms
- `bmi`: Body Mass Index (calculated)
- `profession`: Occupation
- `medical_history`: Relevant medical history
- `study_type`: Type of MRI study
- `sequence_type`: MRI sequence
- `imaging_plane`: Imaging plane
- `clinical_indication`: Reason for study
- `referring_physician`: Doctor who ordered the study
- `date_of_birth`: Patient DOB
- `contact_phone`: Contact number
- `emergency_contact`: Emergency contact information

## Usage

Load a patient file in Python:

```python
import json

with open('data/patients/patient_001_robert_johnson.json', 'r') as f:
    patient_data = json.load(f)
```

## Adding New Patients

To add a new patient:
1. Copy an existing patient file
2. Rename with pattern: `patient_XXX_firstname_lastname.json`
3. Update all fields with new patient data
4. Ensure BMI is calculated correctly: `weight_kg / (height_cm/100)^2`
