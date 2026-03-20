# MIA Prompts Documentation

## Overview

The MIA system uses carefully crafted prompts to guide the LLMs through medical image analysis. This document explains the prompt structure and design principles.

## Prompt Architecture

### Dual-LLM Strategy

- **Gemini 2.5 Flash**: Vision-based analysis requiring image understanding
- **Groq (Llama-3.3-70b)**: Text-based reasoning for report generation and safety

## Gemini Prompts

### 1. Vision Analysis Prompt

**File**: `prompts/gemini_vision_analysis_prompt.md`

**Purpose**: Guide Gemini to analyze MRI images with medical precision.

**Key Sections**:
1. **Role Definition**: Establishes Gemini as an expert radiologist AI
2. **Analysis Framework**: Structured approach to image analysis
3. **Patient Context**: Integrates demographics (age, gender, BMI, profession)
4. **Output Format**: Strict JSON schema for structured results

**Context Variables**:
- `{patient_age}`: Patient's age
- `{patient_gender}`: Patient's gender
- `{patient_bmi}`: Body Mass Index
- `{patient_profession}`: Occupation (for occupational health considerations)

**Output Structure**:
```json
{
  "image_quality": {...},
  "anatomical_structures": {...},
  "findings": [...],
  "differential_diagnosis": [...],
  "recommendations": {...},
  "confidence_score": 0.0-1.0
}
```

---

### 2. Cross-Validation Prompt

**File**: `prompts/gemini_cross_validation_prompt.md`

**Purpose**: Quality assurance through independent re-analysis.

**Key Features**:
- Visual verification of reported findings
- Measurement validation
- Anatomical consistency checks
- Clinical plausibility assessment

**Context Variables**:
- `{original_findings}`: Results from vision analysis
- `{patient_context}`: Patient demographics

**Validation Criteria**:
1. Visual confirmation of findings
2. Measurement accuracy (±10% tolerance)
3. Anatomical plausibility
4. Clinical correlation with patient demographics

---

## Groq Prompts

### 3. Report Generation Prompt

**File**: `prompts/groq_report_generation_prompt.md`

**Purpose**: Generate professional medical reports from analysis data.

**Report Structure**:

**Page 1 - Patient Information**:
- Demographics
- Study details
- Report metadata

**Page 2 - Imaging**:
- MRI image display
- Technical parameters

**Page 3+ - Analysis**:
- Technique description
- Image quality
- Findings with measurements
- Impression
- Differential diagnosis
- Clinical correlation
- Recommendations
- Quality assurance
- Disclaimers

**Context Variables**:
- `{vision_results}`: Gemini vision analysis
- `{validation_results}`: Cross-validation results
- `{patient_info}`: Patient demographics
- `{mri_metadata}`: Study technical details

**Writing Guidelines**:
- Professional medical language
- Evidence-based recommendations
- Clear urgency classification
- Patient-appropriate explanations

---

### 4. Safety Analysis Prompt

**File**: `prompts/groq_safety_analysis_prompt.md`

**Purpose**: Comprehensive safety validation before report finalization.

**Safety Checks**:

1. **Critical Findings** (8 categories):
   - Acute hemorrhage
   - Mass effect
   - Vascular abnormalities
   - Infection/inflammation
   - Fractures
   - Spinal cord compression
   - Acute infarction
   - Hydrocephalus

2. **Confidence Assessment**:
   - Overall confidence score
   - Uncertainty quantification
   - Areas requiring human review

3. **Consistency Validation**:
   - Vision vs. validation alignment
   - Report vs. findings consistency
   - Recommendation appropriateness

4. **Medical Appropriateness**:
   - Evidence-based recommendations
   - Urgency level justification
   - Specialist referral necessity

5. **Patient Safety**:
   - Risk level assessment
   - Immediate action requirements
   - Follow-up urgency

**Output**:
```json
{
  "safety_analysis_summary": {
    "overall_safety_status": "Safe|Review|Unsafe",
    "approval_recommendation": "Approve|Review|Reject",
    "safety_score": 0.0-1.0
  },
  "critical_findings_check": {...},
  "required_actions": [...],
  "escalation_required": {...}
}
```

---

## Prompt Design Principles

### 1. Clarity and Specificity
- Clear role definitions
- Specific task descriptions
- Explicit output formats

### 2. Context Integration
- Patient demographics
- Previous analysis results
- Clinical relevance

### 3. Structured Output
- JSON schemas for parsing
- Consistent field names
- Validation-friendly formats

### 4. Safety First
- Multiple validation layers
- Confidence scoring
- Escalation protocols

### 5. Medical Accuracy
- Evidence-based guidelines
- Professional terminology
- Clinical correlation

---

## Prompt Customization

### Adding New Context Variables

1. Update the prompt template file
2. Modify `PromptLoader` to inject the variable
3. Update documentation

### Example:
```python
# In prompt_loader.py
def get_vision_analysis_prompt(self, patient_info: Dict) -> str:
    prompt = self.load_prompt("gemini_vision_analysis")
    return prompt.format(
        patient_age=patient_info.get("age"),
        patient_gender=patient_info.get("gender"),
        # Add new variable here
        patient_custom_field=patient_info.get("custom_field")
    )
```

---

## Best Practices

1. **Test Prompts Iteratively**: Validate with real data
2. **Version Control**: Track prompt changes
3. **Document Changes**: Update this file when modifying prompts
4. **Monitor Performance**: Track confidence scores and accuracy
5. **User Feedback**: Incorporate clinical feedback

---

## Troubleshooting

### Low Confidence Scores
- Review prompt clarity
- Add more context
- Adjust temperature settings

### Inconsistent Outputs
- Strengthen output format instructions
- Add validation examples
- Lower temperature for consistency

### Missing Information
- Ensure all context variables are provided
- Check prompt template syntax
- Verify data flow in workflow
