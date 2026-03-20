# MIA Main Application - Updated Guide

## Quick Start

Run the MIA workflow:

```bash
.miavenv\Scripts\python.exe main.py
```

## Updated Workflow (4 Steps)

### Step 1: MRI Image Selection 📁

```
📁 Enter MRI image path: data/sample_mri/sample_brain.jpg
```

**What to provide:**
- Full or relative path to MRI image
- Supported: JPEG, PNG, DICOM
- Can drag-and-drop file into terminal

---

### Step 2: Patient Profile Selection 👤 (NEW!)

```
📋 Patient Profile Options:

1. Provide path to patient JSON file
2. Enter custom patient data manually

💡 Example patient files:
   - data/patients/patient_001_robert_johnson.json
   - data/patients/patient_002_maria_garcia.json
   - data/patients/patient_003_david_chen.json
   - data/patients/patient_004_sarah_williams.json
   - data/patients/patient_005_james_thompson.json

📁 Enter patient file path (or 'custom' for manual entry): _
```

**What to provide:**
- **Option 1**: Path to patient JSON file
  - Example: `data/patients/patient_001_robert_johnson.json`
  - Can drag-and-drop file
  - Automatically loads all patient data

- **Option 2**: Type `custom`
  - Manually enter all patient details
  - System will prompt for each field

**Example Input:**
```
📁 Enter patient file path: data/patients/patient_001_robert_johnson.json
✅ Loaded: Robert Johnson
   Study: Brain MRI
```

---

### Step 3: Confirmation ✅

```
📋 Analysis Summary:

👤 Patient: Robert Johnson
   Age: 45, Gender: Male
   BMI: 26.8, Profession: Software Engineer

🏥 Study: Brain MRI
   Sequence: T2
   Plane: Axial

📁 Image: data/sample_mri/sample_brain.jpg

✅ Start analysis? (y/n): _
```

---

### Step 4: Workflow Execution 🚀

```
⏳ Processing through all nodes...
   1️⃣  User Input
   2️⃣  Validation
   3️⃣  Vision Analysis (Gemini)
   4️⃣  Cross-Validation (Gemini)
   5️⃣  Report Generation (Groq)
   6️⃣  Safety Analysis (Groq)
   7️⃣  PDF Generation

[Real-time colored logs...]

✅ No errors - Workflow completed successfully!
```

---

## Key Changes

### ✅ Before (Old Method):
- Select from numbered list (1-5)
- Limited to pre-loaded profiles
- Had to modify code to add patients

### ✅ After (New Method):
- Provide patient file path directly
- Any JSON file can be used
- Easy to add new patients (just create JSON file)
- More flexible and scalable

---

## Usage Examples

### Example 1: Using Existing Patient File
```bash
$ .miavenv\Scripts\python.exe main.py

📁 Enter MRI image path: data/sample_mri/sample_brain.jpg
✅ Image found

📁 Enter patient file path: data/patients/patient_001_robert_johnson.json
✅ Loaded: Robert Johnson
   Study: Brain MRI

✅ Start analysis? (y/n): y
[Processing...]
```

### Example 2: Using Custom Patient Data
```bash
📁 Enter patient file path: custom

📝 Enter Custom Patient Data:
Patient Name: Jane Smith
Age: 50
[... more prompts ...]
```

### Example 3: Drag and Drop
```bash
📁 Enter patient file path: [Drag patient JSON file here]
✅ Loaded: Maria Garcia
```

---

## Patient File Format

Each patient JSON file should contain:

```json
{
    "patient_id": "MIA-P001",
    "name": "Robert Johnson",
    "age": 45,
    "gender": "Male",
    "height_cm": 178,
    "weight_kg": 85,
    "bmi": 26.8,
    "profession": "Software Engineer",
    "study_type": "Brain MRI",
    "sequence_type": "T2",
    "imaging_plane": "Axial",
    "clinical_indication": "Persistent headaches"
}
```

See `data/patients/` for complete examples.

---

## Benefits of File Path Method

1. **Flexibility**: Use any patient file, anywhere
2. **Scalability**: Easy to add unlimited patients
3. **Organization**: Keep patient files organized in folders
4. **Reusability**: Same file can be used multiple times
5. **Version Control**: Track patient file changes
6. **Automation**: Scripts can provide file paths

---

## Error Handling

### File Not Found
```
❌ Error: File not found: wrong_path.json
Try again? (y/n): y
```

### Invalid JSON
```
❌ Error: Invalid JSON file - Expecting property name
Try again? (y/n): y
```

### Missing Fields
- Validation will catch missing required fields
- Workflow will report errors before processing

---

## Tips

1. **Use Tab Completion**: Most terminals support tab completion for paths
2. **Relative Paths**: `data/patients/patient_001.json` works from MIA directory
3. **Absolute Paths**: `C:\MIA\data\patients\patient_001.json` also works
4. **Drag and Drop**: Drag file from explorer into terminal window
5. **Copy Path**: Right-click file → Copy as path

---

## Quick Reference

| Input | What Happens |
|-------|--------------|
| `data/patients/patient_001_robert_johnson.json` | Loads Robert Johnson profile |
| `custom` | Manual entry mode |
| `[Drag file]` | Loads dragged file |
| Empty/Invalid | Error with retry option |

---

## Ready to Use!

The updated workflow is more flexible and professional. Simply provide file paths instead of selecting numbers!

```bash
.miavenv\Scripts\python.exe main.py
```
