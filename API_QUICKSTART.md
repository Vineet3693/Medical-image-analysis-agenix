# MIA FastAPI - Quick Start Guide

## Installation

1. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

2. **Start the API Server**
   ```bash
   # Windows
   run_api.bat
   
   # Or manually
   python -m uvicorn api_main:app --reload --port 8000
   ```

3. **Access API Documentation**
   - Open browser: http://localhost:8000/docs
   - Interactive Swagger UI with all endpoints

## API Usage

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Analyze MRI Image

**Using Swagger UI** (Recommended):
1. Go to http://localhost:8000/docs
2. Find `POST /api/analyze` endpoint
3. Click "Try it out"
4. Upload image file
5. Paste patient data JSON
6. Paste MRI metadata JSON
7. Click "Execute"

**Using curl**:
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "image=@path/to/mri_image.jpg" \
  -F 'patient_data={"name":"John Doe","age":45,"gender":"Male","height_cm":175,"weight_kg":80,"profession":"Engineer"}' \
  -F 'mri_metadata={"study_type":"Brain MRI","sequence_type":"T2","imaging_plane":"Axial"}'
```

### 3. Check Analysis Status
```bash
curl http://localhost:8000/api/reports/MIA-R20260123120000/status
```

### 4. Get Report
```bash
curl http://localhost:8000/api/reports/MIA-R20260123120000
```

### 5. Download PDF
```bash
curl -O http://localhost:8000/api/reports/MIA-R20260123120000/pdf
```

## Example Patient Data

```json
{
  "name": "Robert Johnson",
  "age": 45,
  "gender": "Male",
  "height_cm": 178.0,
  "weight_kg": 85.0,
  "profession": "Software Engineer",
  "medical_history": "No significant history"
}
```

## Example MRI Metadata

```json
{
  "study_type": "Brain MRI",
  "sequence_type": "T2",
  "imaging_plane": "Axial",
  "clinical_indication": "Persistent headaches for 3 months"
}
```

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/health/models` | AI model status |
| POST | `/api/analyze` | Upload & analyze MRI |
| GET | `/api/reports/{id}/status` | Check progress |
| GET | `/api/reports/{id}` | Get report JSON |
| GET | `/api/reports/{id}/pdf` | Download PDF |
| GET | `/api/reports` | List all reports |

## Troubleshooting

**Port already in use:**
```bash
# Change port
python -m uvicorn api_main:app --reload --port 8001
```

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**API keys not configured:**
- Ensure `.env` file has `GEMINI_API_KEY` and `GROQ_API_KEY`
