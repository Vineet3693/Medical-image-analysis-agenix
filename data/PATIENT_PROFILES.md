# Patient Profiles for MIA System

This file contains 5 pre-configured patient profiles for quick testing and demonstration.

## Available Profiles

### Patient 1: Robert Johnson (MIA-P001)
- **Age**: 45, Male
- **BMI**: 26.8 (Overweight)
- **Profession**: Software Engineer
- **Study**: Brain MRI (T2 Axial)
- **Indication**: Persistent headaches for 3 months
- **History**: Hypertension, occasional migraines

### Patient 2: Maria Garcia (MIA-P002)
- **Age**: 52, Female
- **BMI**: 25.0 (Normal)
- **Profession**: Teacher
- **Study**: Lumbar Spine MRI (T1/T2 Sagittal)
- **Indication**: Lower back pain radiating to left leg
- **History**: Type 2 Diabetes, controlled with medication

### Patient 3: David Chen (MIA-P003)
- **Age**: 38, Male
- **BMI**: 25.3 (Normal)
- **Profession**: Accountant
- **Study**: Cervical Spine MRI (T2 Axial)
- **Indication**: Neck pain following motor vehicle accident
- **History**: No significant medical history

### Patient 4: Sarah Williams (MIA-P004)
- **Age**: 61, Female
- **BMI**: 28.1 (Overweight)
- **Profession**: Retired Nurse
- **Study**: Knee MRI (T1 Coronal)
- **Indication**: Right knee pain and swelling
- **History**: Osteoarthritis, previous knee surgery

### Patient 5: James Thompson (MIA-P005)
- **Age**: 29, Male
- **BMI**: 26.3 (Overweight)
- **Profession**: Professional Athlete
- **Study**: Shoulder MRI (T2 Coronal)
- **Indication**: Recurrent shoulder instability
- **History**: Previous shoulder dislocation

## Usage

### Automatic Mode
```bash
.miavenv\Scripts\python.exe run_auto.py
```

The script will:
1. Ask for MRI image path
2. Display available patient profiles
3. Let you select a patient (1-5)
4. Automatically process with selected profile

### Custom Patient
Select `0` when prompted to enter custom patient data instead.

## File Format

The profiles are stored in JSON format at `data/patient_profiles.json` and can be edited to add more patients or modify existing ones.
