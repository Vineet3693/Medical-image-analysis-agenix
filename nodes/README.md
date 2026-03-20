# MIA Nodes Package

This folder contains all the individual node modules for the MIA (Medical Image Analysis) workflow. Each node is a self-contained module that performs a specific task in the analysis pipeline.

## 📁 Node Files

### 1. `mia_vision_analysis_node.py`
**Purpose:** Vision analysis using Gemini 2.5 Flash

**Features:**
- ✅ Input validation (patient info, MRI metadata, image path)
- ✅ Image quality assessment
- ✅ Vision analysis using Gemini 2.5 Flash
- ✅ Measurements extraction
- ✅ Confidence scoring

**Input:**
- `patient_info`: Patient details
- `mri_metadata`: MRI study information
- `mri_image_path`: Path to MRI image

**Output:**
- `vision_analysis`: Dict containing findings, measurements, quality assessment

---

### 2. `mia_cross_validation_node.py`
**Purpose:** Cross-validation using Gemini 2.5 Flash

**Features:**
- ✅ Verify findings from vision analysis
- ✅ Validate measurements for accuracy
- ✅ Identify discrepancies
- ✅ Generate validation recommendations
- ✅ Confidence scoring

**Input:**
- `vision_analysis`: Results from vision analysis node
- `patient_info`: Patient details
- `mri_image_path`: Path to MRI image

**Output:**
- `cross_validation`: Dict containing verified findings, validation status, discrepancies

---

### 3. `mia_report_safety_node.py`
**Purpose:** Report generation and safety analysis using Grok

**Features:**
- ✅ Professional medical report generation
- ✅ Clinical correlation analysis
- ✅ Recommendations generation
- ✅ Critical findings identification
- ✅ Safety score calculation
- ✅ Urgency level assessment

**Input:**
- `vision_analysis`: Vision analysis results
- `cross_validation`: Validation results
- `patient_info`: Patient details
- `mri_metadata`: MRI study information

**Output:**
- `report_content`: Dict containing professional report, clinical correlation, recommendations
- `safety_analysis`: Dict containing critical findings, safety score, urgency level

---

### 4. `mia_pdf_generation_node.py`
**Purpose:** Professional A4 PDF report generation

**Features:**
- ✅ Professional A4-sized PDF formatting
- ✅ Patient demographics section
- ✅ MRI study details
- ✅ Findings presentation
- ✅ Safety warnings and recommendations
- ✅ Watermarks and branding

**Input:**
- `patient_info`: Patient details
- `mri_metadata`: MRI study information
- `vision_analysis`: Vision analysis results
- `cross_validation`: Validation results
- `report_content`: Generated report
- `safety_analysis`: Safety analysis results

**Output:**
- `pdf_path`: Path to generated PDF file

---

## 🔄 Workflow Sequence

```
┌─────────────────────┐
│  User Input         │
│  + Validation       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Vision Analysis    │ → Gemini 2.5 Flash
│  (Node 1)           │   • Image quality
└──────────┬──────────┘   • Findings
           ↓               • Measurements
┌─────────────────────┐
│  Cross Validation   │ → Gemini 2.5 Flash
│  (Node 2)           │   • Verify findings
└──────────┬──────────┘   • Validate measurements
           ↓
┌─────────────────────┐
│  Report & Safety    │ → Grok
│  (Node 3)           │   • Professional report
└──────────┬──────────┘   • Safety analysis
           ↓
┌─────────────────────┐
│  PDF Generation     │ → Professional A4 PDF
│  (Node 4)           │
└─────────────────────┘
```

## 💻 Usage

### Using Individual Nodes

```python
from nodes.mia_vision_analysis_node import vision_analysis_node
from nodes.mia_cross_validation_node import cross_validation_node
from nodes.mia_report_safety_node import report_safety_node
from nodes.mia_pdf_generation_node import pdf_generation_node

# Create initial state
state = {
    "report_id": "MIA-001",
    "patient_info": {...},
    "mri_metadata": {...},
    "mri_image_path": "path/to/image.jpg"
}

# Execute nodes sequentially
state = vision_analysis_node(state)
state = cross_validation_node(state)
state = report_safety_node(state)
state = pdf_generation_node(state)

# Access results
print(f"PDF Report: {state['pdf_path']}")
```

### Using the Complete Workflow

```python
from miaapp import MIAWorkflow

# Create workflow instance
workflow = MIAWorkflow()

# Run complete workflow
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

print(f"PDF Report: {result['pdf_path']}")
```

## 🧪 Testing Individual Nodes

Each node file can be run independently for testing:

```bash
# Test Vision Analysis Node
python nodes/mia_vision_analysis_node.py

# Test Cross Validation Node
python nodes/mia_cross_validation_node.py

# Test Report & Safety Node
python nodes/mia_report_safety_node.py

# Test PDF Generation Node
python nodes/mia_pdf_generation_node.py
```

## 📊 State Structure

The workflow state is a dictionary that flows through all nodes:

```python
{
    "report_id": str,              # Unique report identifier
    "patient_info": dict,          # Patient information
    "mri_metadata": dict,          # MRI study metadata
    "mri_image_path": str,         # Path to MRI image
    "vision_analysis": dict,       # Results from Node 1
    "cross_validation": dict,      # Results from Node 2
    "report_content": dict,        # Results from Node 3 (report)
    "safety_analysis": dict,       # Results from Node 3 (safety)
    "pdf_path": str,               # Results from Node 4
    "current_step": str,           # Current workflow step
    "errors": list                 # List of errors (if any)
}
```

## 🔧 Configuration

Nodes use the following services and configurations:

- **Gemini Service:** `services/gemini_service.py` (for Vision & Cross-validation)
- **Grok Service:** `services/groq_service.py` (for Report & Safety)
- **Prompt Loader:** `utils/prompt_loader.py` (for all AI prompts)
- **Logger:** `utils/logger.py` (for logging)
- **Config:** `config.py` (for output directories and settings)

## 📝 Error Handling

All nodes implement comprehensive error handling:

- Input validation errors are added to `state["errors"]`
- Service initialization errors are caught and logged
- Processing errors are caught, logged, and added to state
- Nodes check for previous errors before processing
- Workflow continues gracefully even if non-critical errors occur

## 🎯 Key Features

- **Modular Design:** Each node is independent and reusable
- **Comprehensive Logging:** Detailed logging at every step
- **Error Resilience:** Graceful error handling and recovery
- **Type Safety:** Proper type hints and validation
- **Documentation:** Extensive comments and docstrings
- **Testability:** Each node can be tested independently

## 📚 Dependencies

Required packages:
- `google-generativeai` (for Gemini)
- `groq` (for Grok)
- `reportlab` (for PDF generation)
- `Pillow` (for image handling)
- `pydantic` (for data models)

## 🚀 Next Steps

1. Run the complete workflow: `python miaapp.py`
2. Test individual nodes for debugging
3. Customize prompts in `prompts/` folder
4. Adjust PDF formatting in `utils/pdf_generator.py`
5. Add custom validation rules in `utils/validators.py`

## 📄 License

MIA Team - Agenix AI © 2026

---

**Version:** 2.0.0  
**Last Updated:** 2026-01-07
