# Interactive MIA Workflow Guide

## Overview

The MIA workflow now **interactively prompts** the user for input instead of using hardcoded values!

## How to Run

### Option 1: Interactive Mode (Recommended)
```bash
.miavenv\Scripts\python.exe run_interactive.py
```

### Option 2: Standard Mode
```bash
.miavenv\Scripts\python.exe mia_langgraph.py
```

Both will now prompt you for input!

## What the Workflow Asks For

### 1. MRI Image Path
```
Enter MRI image path (or press Enter for default):
```
- Provide the full path to your MRI image
- Or press Enter to use: `data/sample_mri/sample.jpg`

### 2. Patient Information
```
--- Patient Information ---
Patient Name (default: John Doe):
Patient Age (default: 45):
Patient Gender (Male/Female, default: Male):
Height in cm (default: 175):
Weight in kg (default: 80):
Profession (default: Engineer):
```
- Enter custom values or press Enter for defaults
- BMI is automatically calculated

### 3. MRI Study Information
```
--- MRI Study Information ---
Study Type (default: Brain MRI):
Sequence Type (default: T2):
Imaging Plane (default: Axial):
```

## Example Session

```
============================================================
MIA - Medical Image Analysis System
============================================================

Please provide the following information:

Enter MRI image path (or press Enter for default): C:\Images\brain_scan.jpg

--- Patient Information ---
Patient Name (default: John Doe): Jane Smith
Patient Age (default: 45): 52
Patient Gender (Male/Female, default: Male): Female
Height in cm (default: 175): 165
Weight in kg (default: 80): 68
Profession (default: Engineer): Teacher

--- MRI Study Information ---
Study Type (default: Brain MRI): Spine MRI
Sequence Type (default: T2): T1
Imaging Plane (default: Axial): Sagittal

============================================================
Report ID: MIA-20260103-163245
============================================================

INFO:nodes:Node: Validation
INFO:nodes:Node: Vision Analysis (Gemini)
...
```

## Features

✅ **Interactive Input**: Prompts for all required data  
✅ **Smart Defaults**: Press Enter to use sensible defaults  
✅ **Auto BMI Calculation**: Calculates BMI from height/weight  
✅ **Report ID Generation**: Automatic unique ID per run  
✅ **User-Friendly**: Clear prompts and formatting  

## Quick Start

1. **Run the interactive script**:
   ```bash
   .miavenv\Scripts\python.exe run_interactive.py
   ```

2. **Provide your MRI image path** when prompted

3. **Enter patient details** (or use defaults)

4. **Wait for analysis** - the workflow will:
   - Validate inputs
   - Analyze with Gemini (if API key configured)
   - Generate report with Groq (if API key configured)
   - Create PDF report

5. **Check results** in `outputs/reports/`

## Notes

- **API Keys Required**: For full functionality, configure:
  - `GEMINI_API_KEY` in `.env`
  - `GROQ_API_KEY` in `.env`

- **Without API Keys**: The workflow will still run but skip LLM analysis steps

- **Validation**: The workflow validates your inputs before processing

## Troubleshooting

**Q: Image not found error?**  
A: Ensure the path you entered exists and is accessible

**Q: Can I skip prompts?**  
A: Yes! Just press Enter to use defaults for all fields

**Q: How do I use my own data?**  
A: Simply type your values when prompted instead of using defaults
