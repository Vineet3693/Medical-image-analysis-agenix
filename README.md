# MIA System - Medical Image Analysis

**Dual-LLM Architecture for Medical Image Analysis**

## Overview

MIA (Medical Image Analysis) is an AI-powered system that analyzes MRI images using a dual-LLM architecture:
- **Gemini 2.5 Flash**: Vision analysis and cross-validation
- **Grok**: Report generation and safety analysis

The system generates professional PDF reports with patient details, MRI images, and comprehensive medical analysis.

## Architecture

```
┌─────────────┐
│ User Input  │ → Patient data + MRI image
└──────┬──────┘
       ↓
┌─────────────┐
│ Validation  │ → Input validation
└──────┬──────┘
       ↓
┌─────────────────────────┐
│ Vision Analysis         │ → Gemini 2.5 Flash
│ (Gemini)                │   • Image quality assessment
└──────┬──────────────────┘   • Anatomical identification
       ↓                       • Abnormality detection
┌─────────────────────────┐   • Measurements
│ Cross Validation        │ → Gemini 2.5 Flash
│ (Gemini)                │   • Verify findings
└──────┬──────────────────┘   • Validate measurements
       ↓                       • Check consistency
┌─────────────────────────┐
│ Report Generation       │ → Grok
│ (Grok)                  │   • Professional report
└──────┬──────────────────┘   • Clinical correlation
       ↓                       • Recommendations
┌─────────────────────────┐
│ Safety Analysis         │ → Grok
│ (Grok)                  │   • Critical findings check
└──────┬──────────────────┘   • Confidence assessment
       ↓                       • Quality control
┌─────────────────────────┐
│ PDF Generation          │ → Professional A4 PDF
└─────────────────────────┘   • Patient details
                              • MRI images
                              • Detailed analysis
```

## Features

### Gemini 2.5 Flash (Vision & Validation)
- **Vision Analysis**: Comprehensive MRI image analysis
  - Image quality assessment
  - Anatomical structure identification
  - Abnormality detection and localization
  - Precise measurements and quantification
  - Differential diagnosis suggestions

- **Cross-Validation**: Quality assurance
  - Visual verification of findings
  - Measurement validation
  - Anatomical consistency checks
  - Clinical plausibility assessment

### Grok (Report & Safety)
- **Report Generation**: Professional medical reports
  - Structured medical language
  - Clinical correlation with patient demographics
  - Evidence-based recommendations
  - Patient-friendly explanations

- **Safety Analysis**: Comprehensive safety validation
  - Critical finding identification
  - Confidence and uncertainty assessment
  - Risk assessment and urgency classification
  - Quality control checks
  - Medical disclaimer generation

### PDF Report Features
- **Page 1**: Patient Information
  - Name, age, gender, BMI, height, profession
  - Study details and metadata
  
- **Page 2**: MRI Image Display
  - High-quality MRI image embedding
  - Technical parameters
  - Image quality assessment

- **Page 3+**: Detailed Analysis
  - Findings with measurements
  - Impression and differential diagnosis
  - Clinical correlation (age, profession, BMI)
  - Recommendations and urgency level
  - Quality assurance metrics
  - Medical disclaimers

- **Professional Formatting**:
  - A4 format (210mm × 297mm)
  - MIA Team - Agenix AI branding
  - Watermark with logo
  - Professional fonts and colors
  - Header and footer on each page

## Installation

1. **Clone the repository**:
```bash
cd e:\MIA
```

2. **Create virtual environment**:
```bash
python -m venv .miavenv
.miavenv\Scripts\activate  # Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
copy .env.example .env
# Edit .env and add your API keys:
# GEMINI_API_KEY=your_gemini_key
# XAI_API_KEY=your_xai_key
```

5. **Add your logo** (optional):
```bash
# Place your logo file in:
# e:\MIA\assets\logo.png
```

## Usage

### Quick Start

```python
from example_usage import main

# Run the example workflow
main()
```

### Custom Usage

```python
from models.patient_data_schema import PatientInfo, MRIMetadata, Gender
from utils.pdf_generator import generate_mia_report
from datetime import datetime

# 1. Create patient information
patient = PatientInfo(
    name="Jane Smith",
    patient_id="MIA-001",
    age=52,
    gender=Gender.FEMALE,
    height_cm=165,
    weight_kg=68,
    bmi=25.0,
    profession="Teacher"
)

# 2. Create MRI metadata
mri_metadata = MRIMetadata(
    study_date=datetime.now(),
    study_type="Brain MRI",
    sequence_type="T2",
    imaging_plane="Axial",
    image_quality="Excellent"
)

# 3. Run workflow (see example_usage.py for complete workflow)
# ...

# 4. Generate PDF report
# pdf_path = generate_mia_report(mia_report, output_dir)
```

## Project Structure

```
e:\MIA\
├── prompts/                          # LLM prompts
│   ├── gemini_vision_analysis_prompt.md
│   ├── gemini_cross_validation_prompt.md
│   ├── grok_report_generation_prompt.md
│   └── grok_safety_analysis_prompt.md
├── models/                           # Data models
│   └── patient_data_schema.py
├── utils/                            # Utilities
│   ├── prompt_loader.py
│   └── pdf_generator.py
├── assets/                           # Assets (logo, etc.)
│   └── logo.png (user-provided)
├── outputs/                          # Generated outputs
│   ├── reports/                      # PDF reports
│   ├── images/                       # Processed images
│   └── logs/                         # System logs
├── config.py                         # Configuration
├── requirements.txt                  # Dependencies
├── .env.example                      # Environment template
├── example_usage.py                  # Usage example
└── README.md                         # This file
```

## Configuration

Edit `config.py` to customize:
- LLM settings (Gemini and Grok)
- PDF formatting (fonts, colors, layout)
- Workflow configuration
- Output settings

## Prompts

The system uses carefully crafted prompts for each LLM:

### Gemini Prompts
1. **Vision Analysis**: Comprehensive MRI analysis framework
2. **Cross-Validation**: Quality assurance and verification

### Grok Prompts
1. **Report Generation**: Professional medical report structure
2. **Safety Analysis**: Safety validation and risk assessment

All prompts are in `prompts/` directory and can be customized.

## API Keys

You need two API keys:

1. **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **X.AI API Key** (for Grok): Get from [X.AI Console](https://console.x.ai/)

Add them to `.env` file:
```
GEMINI_API_KEY=your_gemini_key_here
XAI_API_KEY=your_xai_key_here
```

## Next Steps

1. **Provide Logo**: Add your logo to `assets/logo.png` for watermark
2. **Configure API Keys**: Set up `.env` with your API keys
3. **Integrate LangGraph**: Update `mia langgraph.py` with actual LLM calls
4. **Test with Real Data**: Test with actual MRI images
5. **Customize Prompts**: Adjust prompts for your specific use case

## Requirements

- Python 3.9+
- Gemini API access
- X.AI API access (for Grok)
- See `requirements.txt` for full dependencies

## License

Proprietary - Agenix AI MIA Team

## Contact

MIA Team - Agenix AI
Email: mia-team@agenix.ai

---

**Version**: 1.0.0
**Last Updated**: 2026-01-01
