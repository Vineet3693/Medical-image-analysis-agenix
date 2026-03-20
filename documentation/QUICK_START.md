# Quick Start Guide - MIA System

## 🚀 Fastest Way to Run

```bash
.miavenv\Scripts\python.exe run_auto.py
```

## What You'll Be Asked

### 1. MRI Image Path
```
Enter MRI image path: C:\path\to\your\mri_image.jpg
```

### 2. Select Patient (1-5)
```
Available Patient Profiles
============================================================

1. Robert Johnson
   Age: 45, Gender: Male
   Study: Brain MRI
   Indication: Persistent headaches for 3 months

2. Maria Garcia
   Age: 52, Gender: Female
   Study: Lumbar Spine MRI
   Indication: Lower back pain radiating to left leg

3. David Chen
   Age: 38, Gender: Male
   Study: Cervical Spine MRI
   Indication: Neck pain following motor vehicle accident

4. Sarah Williams
   Age: 61, Gender: Female
   Study: Knee MRI
   Indication: Right knee pain and swelling

5. James Thompson
   Age: 29, Gender: Male
   Study: Shoulder MRI
   Indication: Recurrent shoulder instability

Select patient (1-5) or 0 to enter custom: 1
```

### 3. Automatic Processing

The system will automatically:
- ✅ Validate the image
- ✅ Analyze with Gemini AI (vision)
- ✅ Cross-validate findings
- ✅ Generate report with Groq AI
- ✅ Perform safety analysis
- ✅ Create PDF report

### 4. Get Results

```
============================================================
WORKFLOW COMPLETED
============================================================
Patient: Robert Johnson
Report ID: MIA-20260103-164530
PDF Path: outputs/reports/MIA-20260103-164530.pdf
✅ Analysis completed successfully!
============================================================
```

## That's It!

Just provide the image path and select a patient. Everything else is automatic!

## Alternative Modes

### Interactive Mode (Custom Patient)
```bash
.miavenv\Scripts\python.exe run_interactive.py
```
Asks for all patient details manually.

### Standard Mode
```bash
.miavenv\Scripts\python.exe mia_langgraph.py
```
Same as interactive mode.

## API Keys

✅ **Already Configured!**
- Gemini API: Ready
- Groq API: Ready

No additional setup needed!
