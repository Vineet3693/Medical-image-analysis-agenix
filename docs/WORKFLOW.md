# MIA Workflow Documentation

## Overview

The MIA workflow orchestrates a 7-step process for medical image analysis using LangGraph state management.

## Workflow Architecture

```
┌─────────────┐
│ User Input  │ → Initialize report, collect data
└──────┬──────┘
       ↓
┌─────────────┐
│ Validation  │ → Validate patient data, MRI image
└──────┬──────┘
       ↓
┌─────────────────────────┐
│ Vision Analysis         │ → Gemini 2.5 Flash
│ (Gemini)                │   Analyze MRI image
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│ Cross Validation        │ → Gemini 2.5 Flash
│ (Gemini)                │   Verify findings
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│ Report Generation       │ → Groq (Llama-3.3-70b)
│ (Groq)                  │   Generate medical report
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│ Safety Analysis         │ → Groq (Llama-3.3-70b)
│ (Groq)                  │   Safety validation
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│ PDF Generation          │ → ReportLab
│                         │   Create final PDF
└─────────────────────────┘
```

## State Management

### MIAState TypedDict

The workflow maintains state across all nodes:

```python
class MIAState(TypedDict):
    # Input
    patient_info: Dict[str, Any]
    mri_metadata: Dict[str, Any]
    mri_image_path: str
    
    # Processing
    vision_analysis: Dict[str, Any]
    cross_validation: Dict[str, Any]
    report_content: Dict[str, Any]
    safety_analysis: Dict[str, Any]
    
    # Output
    report_id: str
    pdf_path: str
    
    # Status
    current_step: str
    errors: List[str]
```

## Node Descriptions

### 1. User Input Node

**Function**: `user_input_node(state: MIAState) -> MIAState`

**Purpose**: Initialize the workflow and generate a unique report ID.

**Actions**:
- Generate report ID: `MIA-YYYYMMDD-HHMMSS`
- Set current step to "user_input"
- Return updated state

**No external API calls**

---

### 2. Validation Node

**Function**: `validation_node(state: MIAState) -> MIAState`

**Purpose**: Validate all input data before processing.

**Validations**:
- Patient info completeness (name, age, gender, etc.)
- MRI metadata completeness (study type, sequence, plane)
- Image file existence and readability

**Error Handling**:
- Collects all validation errors in `state["errors"]`
- Logs validation failures
- Allows workflow to continue (errors checked in subsequent nodes)

---

### 3. Vision Node

**Function**: `vision_node(state: MIAState) -> MIAState`

**Purpose**: Analyze MRI image using Gemini vision capabilities.

**Process**:
1. Check for validation errors (skip if errors exist)
2. Initialize Gemini service
3. Load vision analysis prompt with patient context
4. Call Gemini API with image and prompt
5. Parse JSON response
6. Store results in `state["vision_analysis"]`

**API**: Google Gemini 2.5 Flash

**Output**:
- Image quality assessment
- Anatomical structures identified
- Findings with measurements
- Differential diagnoses
- Confidence score

---

### 4. Cross-Validation Node

**Function**: `cross_validation_node(state: MIAState) -> MIAState`

**Purpose**: Independent verification of vision analysis results.

**Process**:
1. Check for previous errors
2. Initialize Gemini service
3. Load cross-validation prompt with vision results
4. Call Gemini API for re-analysis
5. Compare with original findings
6. Store validation results

**API**: Google Gemini 2.5 Flash

**Validation Checks**:
- Visual confirmation of findings
- Measurement accuracy
- Anatomical consistency
- Clinical plausibility

---

### 5. Report Node

**Function**: `report_node(state: MIAState) -> MIAState`

**Purpose**: Generate comprehensive medical report.

**Process**:
1. Check for previous errors
2. Initialize Groq service
3. Load report generation prompt with all analysis data
4. Call Groq API
5. Parse report content
6. Store in `state["report_content"]`

**API**: Groq (Llama-3.3-70b-versatile)

**Report Sections**:
- Patient demographics
- Study information
- Technique description
- Findings
- Impression
- Differential diagnosis
- Clinical correlation
- Recommendations

---

### 6. Safety Node

**Function**: `safety_node(state: MIAState) -> MIAState`

**Purpose**: Comprehensive safety validation.

**Process**:
1. Check for previous errors
2. Initialize Groq service
3. Load safety analysis prompt
4. Call Groq API
5. Evaluate safety status
6. Store safety results

**API**: Groq (Llama-3.3-70b-versatile)

**Safety Checks**:
- Critical finding identification
- Confidence assessment
- Consistency validation
- Medical appropriateness
- Patient safety risk
- Escalation requirements

---

### 7. PDF Node

**Function**: `pdf_node(state: MIAState) -> MIAState`

**Purpose**: Generate final PDF report.

**Process**:
1. Check for previous errors
2. Assemble complete MIAReport object
3. Call PDF generator
4. Save PDF to outputs/reports/
5. Store PDF path in state

**No API calls** (local PDF generation)

**PDF Structure**:
- Page 1: Patient information
- Page 2: MRI image
- Page 3+: Detailed analysis

---

## Workflow Execution

### Running the Workflow

```python
from mia_langgraph import create_mia_workflow

# Create workflow
app = create_mia_workflow()

# Define initial state
initial_state = {
    "patient_info": {...},
    "mri_metadata": {...},
    "mri_image_path": "path/to/image.jpg",
    "errors": []
}

# Execute workflow
result = app.invoke(initial_state)

# Check results
print(f"Report ID: {result['report_id']}")
print(f"PDF Path: {result['pdf_path']}")
if result.get("errors"):
    print(f"Errors: {result['errors']}")
```

### Error Handling Strategy

1. **Validation Errors**: Collected but don't stop workflow
2. **API Errors**: Logged and added to errors list
3. **Node Errors**: Subsequent nodes check for errors before processing
4. **Final Check**: Review errors list before PDF generation

---

## Configuration

Workflow configuration in `config.py`:

```python
WORKFLOW_CONFIG = {
    "nodes": {
        "user_input": {...},
        "validation": {...},
        "vision": {"llm": "gemini", "prompt": "gemini_vision_analysis"},
        "cross_validation": {"llm": "gemini", "prompt": "gemini_cross_validation"},
        "report": {"llm": "groq", "prompt": "groq_report_generation"},
        "safety": {"llm": "groq", "prompt": "groq_safety_analysis"},
        "pdf_generation": {...}
    },
    "flow": [
        "user_input",
        "validation",
        "vision",
        "cross_validation",
        "report",
        "safety",
        "pdf_generation"
    ]
}
```

---

## Monitoring and Logging

All nodes log their execution:

```python
logger.info("Node: Vision Analysis (Gemini)")
logger.info("Vision analysis completed successfully")
logger.error(f"Vision analysis failed: {e}")
```

Logs are stored in `outputs/logs/`

---

## Performance Considerations

### Typical Execution Time

- User Input: <1s
- Validation: <1s
- Vision Analysis: 5-15s (Gemini API)
- Cross-Validation: 5-15s (Gemini API)
- Report Generation: 3-10s (Groq API)
- Safety Analysis: 3-10s (Groq API)
- PDF Generation: 1-3s

**Total**: ~20-60 seconds per report

### Optimization Tips

1. **Parallel Processing**: Vision and validation could run in parallel
2. **Caching**: Cache prompts to reduce load time
3. **Batch Processing**: Process multiple images in sequence
4. **API Optimization**: Use streaming for faster responses

---

## Extending the Workflow

### Adding a New Node

1. Define node function in `nodes.py`:
```python
def new_node(state: MIAState) -> MIAState:
    logger.info("Node: New Node")
    # Process state
    return state
```

2. Add to workflow in `mia_langgraph.py`:
```python
workflow.add_node("new_node", new_node)
workflow.add_edge("previous_node", "new_node")
workflow.add_edge("new_node", "next_node")
```

3. Update configuration in `config.py`

4. Update documentation

---

## Troubleshooting

### Workflow Hangs
- Check API connectivity
- Verify API keys in `.env`
- Review logs for errors

### Validation Failures
- Ensure all required patient fields are provided
- Verify MRI image path is correct
- Check image file format

### API Errors
- Verify API keys are valid
- Check API rate limits
- Review prompt formatting

### PDF Generation Fails
- Ensure output directory exists
- Check logo file is present
- Verify all data is complete
