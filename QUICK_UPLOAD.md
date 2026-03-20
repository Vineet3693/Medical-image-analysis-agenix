# ✅ QUICK UPLOAD GUIDE - Copy & Paste Ready

## 🎯 What You Need to Upload

Go to: **http://127.0.0.1:8000/docs**

Find: **POST /api/analyze** → Click **"Try it out"**

---

## 📋 Fill These 4 Fields:

### 1️⃣ image (REQUIRED)
- Click "Choose File"
- Select your MRI scan image (.jpg, .png, or .dcm file)

### 2️⃣ patient_data (REQUIRED)
**Copy this JSON and edit the values:**

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

⚠️ **Important**: 
- Use decimal numbers: `175.0` not `175`
- Age is a number: `45` not `"45"`
- All field names in double quotes

### 3️⃣ mri_metadata (REQUIRED)
**Copy this JSON and edit the values:**

```json
{
  "study_type": "Brain MRI",
  "sequence_type": "T2",
  "imaging_plane": "Axial",
  "clinical_indication": "Persistent headaches"
}
```

### 4️⃣ medical_report (OPTIONAL)
- Click "Choose File" if you have a medical report PDF/TXT
- Or leave empty if you don't have one

---

## 🚀 After Clicking "Execute"

### ✅ Success Response (Status 200):
```json
{
  "report_id": "MIA-R20260123143000",
  "status": "processing",
  "message": "Analysis workflow started successfully",
  "patient_name": "John Doe"
}
```

**Save the `report_id`!** You need it to:
- Check status: `GET /api/reports/{report_id}/status`
- Download PDF: `GET /api/reports/{report_id}/pdf`

### ❌ Error Response (Status 400):
If you get an error, check:
1. ✅ Image file is selected
2. ✅ JSON has double quotes around field names
3. ✅ Numbers are numbers (not strings)
4. ✅ Decimal points for height/weight (175.0, not 175)

---

## 📥 Download Your Report

1. Wait 2-3 minutes for analysis to complete
2. Go to: `GET /api/reports/{report_id}/pdf`
3. Replace `{report_id}` with your actual report ID
4. Click "Try it out" → "Execute"
5. Click "Download file"

---

## 🔍 Common Errors Fixed

### Error: "Invalid JSON"
❌ Wrong:
```json
{
  name: "John",  // Missing quotes
  age: "45"      // Age should be number
}
```

✅ Correct:
```json
{
  "name": "John",
  "age": 45
}
```

### Error: "Missing required field"
Make sure you have ALL these fields in patient_data:
- name
- age
- gender
- height_cm
- weight_kg

---

## 💡 Pro Tips

1. **Validate your JSON** at https://jsonlint.com before pasting
2. **Use the examples above** - just change the values
3. **Don't add extra commas** at the end of the last field
4. **Use double quotes** (") not single quotes (')
5. **Numbers don't need quotes** - age: 45 not age: "45"

---

## 🆘 Still Having Issues?

The API is running and healthy! ✅

If you're getting 400 errors, it's usually a JSON formatting issue.

**Share with me:**
1. The exact JSON you're using
2. The error message you see
3. Screenshot of the error (if possible)

I'll help you fix it immediately!
