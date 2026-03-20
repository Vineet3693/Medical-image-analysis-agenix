# How to Upload MRI Image and Medical Report for Analysis

## Step-by-Step Guide

### 1. Open the API Documentation
- Go to: **http://127.0.0.1:8000/docs**
- The Swagger UI will open

### 2. Find the Analysis Endpoint
- Scroll down to the **"Analysis"** section
- Click on **"POST /api/analyze"** to expand it

### 3. Click "Try it out"
- Click the blue **"Try it out"** button in the top right

### 4. Upload Your Files and Data

You'll see **4 input fields**:

#### Field 1: `image` (REQUIRED) ⭐
- **What**: Your MRI scan image
- **How**: Click "Choose File" button
- **Formats**: JPEG, PNG, DICOM
- **Example**: `brain_mri.jpg`, `scan.png`

#### Field 2: `patient_data` (REQUIRED) ⭐
- **What**: Patient information as JSON
- **How**: Copy and paste the JSON below, then edit with your patient's details
```json
{
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "height_cm": 175.0,
  "weight_kg": 80.0,
  "profession": "Engineer",
  "medical_history": "No significant history"
}
```

#### Field 3: `mri_metadata` (REQUIRED) ⭐
- **What**: MRI study information as JSON
- **How**: Copy and paste the JSON below, then edit with your study details
```json
{
  "study_type": "Brain MRI",
  "sequence_type": "T2",
  "imaging_plane": "Axial",
  "clinical_indication": "Persistent headaches"
}
```

#### Field 4: `medical_report` (OPTIONAL) 📄
- **What**: Patient's medical report/history document
- **How**: Click "Choose File" button
- **Formats**: PDF, TXT, DOCX
- **Example**: `patient_medical_history.pdf`, `previous_reports.txt`
- **Note**: This is optional - only upload if you have additional medical documents

### 5. Execute the Analysis
- Click the blue **"Execute"** button
- Wait for the response

### 6. Get Your Report ID
The response will show:
```json
{
  "report_id": "MIA-R20260123135800",
  "status": "processing",
  "message": "Analysis workflow started successfully",
  "patient_name": "John Doe"
}
```

**Save this `report_id`** - you'll need it to check status and download the PDF!

### 7. Check Analysis Status
- Use endpoint: **GET /api/reports/{report_id}/status**
- Replace `{report_id}` with your actual report ID
- Keep checking until status is "completed"

### 8. Download Your PDF Report
- Use endpoint: **GET /api/reports/{report_id}/pdf**
- Replace `{report_id}` with your actual report ID
- Click "Execute" and then "Download file"

---

## Quick Example

### Minimum Required Upload:
1. **MRI Image**: `brain_scan.jpg`
2. **Patient Data**:
   ```json
   {
     "name": "Jane Smith",
     "age": 35,
     "gender": "Female",
     "height_cm": 165.0,
     "weight_kg": 60.0,
     "profession": "Teacher"
   }
   ```
3. **MRI Metadata**:
   ```json
   {
     "study_type": "Brain MRI",
     "sequence_type": "T2",
     "imaging_plane": "Axial"
   }
   ```

### With Medical Report (Optional):
Add a 4th file:
- **Medical Report**: `patient_history.pdf`

---

## What Happens After Upload?

1. ✅ Files are saved to `data/uploads/`
2. 🔄 AI analysis starts automatically in background
3. 📊 Vision analysis (Gemini AI)
4. ✓ Cross-validation (Gemini AI)
5. 📝 Report generation (Groq AI)
6. 🛡️ Safety analysis
7. 📄 PDF report created
8. ✅ Ready to download!

---

## Troubleshooting

**"No file chosen"**
- Make sure you clicked the "Choose File" button and selected a file

**"Invalid JSON"**
- Check that your JSON has proper quotes and commas
- Use the examples above as templates

**"Missing required field"**
- Make sure all 3 required fields are filled:
  - image file
  - patient_data JSON
  - mri_metadata JSON

**Server not responding**
- Make sure the server is running: `run_api.bat`
- Check the URL is correct: `http://127.0.0.1:8000/docs`
