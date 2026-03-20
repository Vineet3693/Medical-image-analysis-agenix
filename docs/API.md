# MIA API Documentation

## Overview

The MIA (Medical Image Analysis) system provides a comprehensive API for analyzing medical images using a dual-LLM architecture.

## Core Services

### Gemini Service

**Purpose**: Vision analysis and cross-validation of MRI images.

#### Methods

##### `perform_vision_analysis(image_path: str, prompt: str) -> Dict[str, Any]`

Analyzes an MRI image using Gemini 2.5 Flash vision capabilities.

**Parameters**:
- `image_path`: Path to the MRI image file
- `prompt`: Formatted vision analysis prompt

**Returns**: Dictionary containing:
- `image_quality`: Overall quality assessment
- `anatomical_structures`: Identified structures
- `findings`: List of detected findings
- `differential_diagnosis`: Possible diagnoses
- `confidence_score`: Analysis confidence (0-1)

**Example**:
```python
from services import get_gemini_service
from utils import PromptLoader

gemini = get_gemini_service()
loader = PromptLoader()

prompt = loader.get_vision_analysis_prompt(patient_info)
results = gemini.perform_vision_analysis("path/to/mri.jpg", prompt)
```

##### `perform_cross_validation(image_path: str, prompt: str) -> Dict[str, Any]`

Cross-validates vision analysis results.

**Parameters**:
- `image_path`: Path to the MRI image file
- `prompt`: Formatted cross-validation prompt with original results

**Returns**: Dictionary containing validation results and approval status.

---

### Groq Service

**Purpose**: Medical report generation and safety analysis.

#### Methods

##### `generate_report(prompt: str) -> Dict[str, Any]`

Generates a comprehensive medical report.

**Parameters**:
- `prompt`: Formatted report generation prompt with all analysis data

**Returns**: Dictionary containing:
- `report_metadata`: Report ID, generation date
- `page_1_patient_info`: Patient demographics
- `page_3_analysis`: Detailed findings and recommendations

**Example**:
```python
from services import get_groq_service

groq = get_groq_service()
report = groq.generate_report(report_prompt)
```

##### `perform_safety_analysis(prompt: str) -> Dict[str, Any]`

Performs safety validation on the generated report.

**Parameters**:
- `prompt`: Formatted safety analysis prompt

**Returns**: Dictionary containing safety assessment and approval recommendation.

---

## Utilities

### PromptLoader

**Purpose**: Load and format prompts with context injection.

#### Methods

##### `get_vision_analysis_prompt(patient_info: Dict) -> str`

Loads and formats the vision analysis prompt.

##### `get_cross_validation_prompt(vision_results: Dict, patient_info: Dict) -> str`

Loads and formats the cross-validation prompt.

##### `get_report_generation_prompt(vision_results: Dict, validation_results: Dict, patient_info: Dict, mri_metadata: Dict) -> str`

Loads and formats the report generation prompt.

##### `get_safety_analysis_prompt(vision_results: Dict, validation_results: Dict, report_content: Dict, patient_info: Dict) -> str`

Loads and formats the safety analysis prompt.

---

### PDF Generator

**Purpose**: Generate professional PDF reports.

#### Functions

##### `generate_mia_report(report: MIAReport, output_dir: str) -> str`

Generates a complete PDF report.

**Parameters**:
- `report`: MIAReport object with all data
- `output_dir`: Directory to save the PDF

**Returns**: Path to the generated PDF file.

**Example**:
```python
from utils import generate_mia_report
from models import MIAReport

pdf_path = generate_mia_report(mia_report, "outputs/reports")
```

---

## Workflow

### LangGraph Nodes

The workflow consists of 7 nodes defined in `nodes.py`:

1. **user_input_node**: Collects initial data and generates report ID
2. **validation_node**: Validates patient data and image path
3. **vision_node**: Performs Gemini vision analysis
4. **cross_validation_node**: Validates results with Gemini
5. **report_node**: Generates report with Groq
6. **safety_node**: Performs safety analysis with Groq
7. **pdf_node**: Generates final PDF report

### State Management

The workflow uses `MIAState` TypedDict to maintain state across nodes:

```python
class MIAState(TypedDict):
    patient_info: Dict[str, Any]
    mri_metadata: Dict[str, Any]
    mri_image_path: str
    vision_analysis: Dict[str, Any]
    cross_validation: Dict[str, Any]
    report_content: Dict[str, Any]
    safety_analysis: Dict[str, Any]
    report_id: str
    pdf_path: str
    current_step: str
    errors: List[str]
```

---

## Configuration

All configuration is centralized in `config.py`:

- **GEMINI_CONFIG**: Gemini API settings
- **GROQ_CONFIG**: Groq API settings
- **PDF_CONFIG**: PDF generation settings
- **WORKFLOW_CONFIG**: Node definitions and flow
- **OUTPUT_CONFIG**: Output directories

---

## Error Handling

All nodes implement error handling:
- Errors are collected in `state["errors"]`
- Nodes check for errors before processing
- Detailed logging for debugging

---

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Test coverage includes:
- Model validation
- Prompt loading
- PDF generation
- Workflow execution
