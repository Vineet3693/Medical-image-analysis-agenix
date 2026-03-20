# MIA Enhanced Features - Quick Start Guide

## 🚀 Quick Start

### Option 1: Run with Batch Script (Easiest)

```bash
cd e:\MIA
run_mia.bat
```

### Option 2: Run Directly

```bash
cd e:\MIA
.miavenv\Scripts\python.exe miaapp.py
```

### Option 3: Run Test Script

```bash
.miavenv\Scripts\python.exe test_enhanced_features.py
```

---

## 🎯 What's New

### 1. Automatic Patient Data Loading from JSON
- **Load patient data from JSON files** - No manual entry needed!
- Just select a patient file from `data/patients/` directory
- All patient info and study metadata loaded automatically

### 2. Automatic Image Type Classification
- **Gemini 2.5 Flash** automatically detects medical image type
- Supports: MRI, X-Ray, CT, Ultrasound, PET, Mammography, and more
- Classification happens FIRST before any analysis

### 3. Groq Cross-Validation
- **Groq LLM** independently validates Gemini's findings
- Generates comparison matrix showing AI consensus
- Provides enhanced confidence through dual-AI validation

---

## 📋 Workflow

When you run the application:

1. **Provide Image Path** - Enter path to your medical image
2. **Choose Patient Data Source:**
   - **Option 1:** Load from JSON file (recommended)
     - Select from available patient files
     - All data loaded automatically
   - **Option 2:** Enter manually
     - Input patient details one by one

3. **Automatic Processing:**
   - ✅ Image type classification (MRI, X-Ray, CT, etc.)
   - ✅ Vision analysis by Gemini
   - ✅ Cross-validation by Gemini
   - ✅ Independent validation by Groq
   - ✅ Comparison matrix generation
   - ✅ Professional report generation
   - ✅ Safety analysis
   - ✅ PDF report creation

---

## 📁 Patient JSON File Format

Place patient JSON files in `e:\MIA\data\patients\`:

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
  "medical_history": "Hypertension, occasional migraines",
  "study_type": "Brain MRI",
  "sequence_type": "T2",
  "imaging_plane": "Axial",
  "clinical_indication": "Persistent headaches for 3 months",
  "referring_physician": "Dr. Sarah Mitchell"
}
```

---

## 📋 Example Usage

### Python API

```python
from miaapp import MIAWorkflow

workflow = MIAWorkflow()
result = workflow.run(
    patient_info={
        "name": "John Doe",
        "age": 45,
        "gender": "Male",
        "height_cm": 175.0,
        "weight_kg": 80.0,
        "bmi": 26.1,
        "profession": "Engineer"
    },
    mri_metadata={
        "study_type": "Brain MRI",
        "sequence_type": "T2",
        "imaging_plane": "Axial"
    },
    mri_image_path="data/sample_mri/sample.jpg"
)

# Access new features
image_type = result["image_classification"]["image_type"]
print(f"Detected Image Type: {image_type}")

consensus = result["cross_validation"]["groq_validation"]["groq_validation_summary"]["consensus_score"]
print(f"AI Consensus Score: {consensus:.2%}")
```

---

## 📊 Expected Output

```
🔍 Image Classification:
   • Type: MRI
   • Sub-Type: Brain MRI T2-weighted
   • Confidence: 95.00%
   • Region: Brain/Head

🤖 Groq Cross-Validation:
   • Consensus Score: 90.00%
   • Agreements: 4
   • Disagreements: 0
   • Overall Confidence: 92.00%
```

---

## ⚙️ Configuration

Ensure your `.env` file has both API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

---

## 📁 Key Files

- **Vision Analysis:** `nodes/mia_vision_analysis_node.py`
- **Cross-Validation:** `nodes/mia_cross_validation_node.py`
- **Groq Service:** `services/groq_service.py`
- **Test Script:** `test_enhanced_features.py`
- **Prompts:**
  - `prompts/gemini_image_classification_prompt.md`
  - `prompts/groq_cross_validation_prompt.md`

---

## 🔍 Workflow Steps

1. **User Input** - Provide patient info and image
2. **Image Classification** - Gemini detects image type (NEW)
3. **Vision Analysis** - Gemini analyzes the image
4. **Gemini Cross-Validation** - Gemini validates findings
5. **Groq Cross-Validation** - Groq independently validates (NEW)
6. **Report Generation** - Groq generates professional report
7. **Safety Analysis** - Groq performs safety checks
8. **PDF Generation** - Creates final PDF report

---

## 💡 Tips

- **High Consensus (≥85%)**: Proceed with confidence
- **Moderate Consensus (70-84%)**: Review discrepancies
- **Low Consensus (<70%)**: Manual expert review recommended

---

## 📖 Full Documentation

See [walkthrough.md](file:///C:/Users/VINEET%20YADAV/.gemini/antigravity/brain/c0bfdafa-5aef-4a9a-93fd-a8e521aa9cbc/walkthrough.md) for complete documentation.
