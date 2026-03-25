"""
Test short and long report types via the MIA API.
Tests /api/analyze endpoint with report_type='short' and 'long'.
"""
import json
import time
import os
import urllib.request
import urllib.parse

BASE = "http://localhost:8080"

# ─── helper ──────────────────────────────────────────────────────────────────
def req(method, path, **kwargs):
    url = BASE + path
    r = urllib.request.Request(url, method=method, **kwargs)
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read())


def submit_analysis(image_path: str, report_type: str) -> str:
    """Submit an analysis job and return the report_id."""
    import http.client, mimetypes
    boundary = "----MIATestBoundary"
    patient_data = json.dumps({
        "name": "Test Patient",
        "age": 40,
        "gender": "Male",
        "height_cm": 175.0,
        "weight_kg": 75.0,
        "bmi": 24.5,
        "profession": "Engineer"
    })
    mri_meta = json.dumps({
        "study_type": "Brain MRI",
        "sequence_type": "T2",
        "imaging_plane": "Axial"
    })

    # Build multipart body
    body_parts = []
    def add_field(name, value):
        body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}')

    def add_file(name, filepath, content_type="image/jpeg"):
        with open(filepath, "rb") as f:
            file_bytes = f.read()
        filename = os.path.basename(filepath)
        body_parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: {content_type}\r\n\r\n'
        )
        return file_bytes

    add_field("patient_data", patient_data)
    add_field("mri_metadata", mri_meta)
    add_field("report_type", report_type)

    # Encode text parts
    encoded = "\r\n".join(body_parts).encode("utf-8")
    file_bytes = add_file("image", image_path)
    final_body = (
        "\r\n".join(body_parts).encode("utf-8")
        + b"\r\n"
        + f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{os.path.basename(image_path)}"\r\nContent-Type: image/jpeg\r\n\r\n'.encode("utf-8")
        + file_bytes
        + f"\r\n--{boundary}--\r\n".encode("utf-8")
    )

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(final_body)),
    }

    conn = http.client.HTTPConnection("localhost", 8080)
    conn.request("POST", "/api/analyze", body=final_body, headers=headers)
    resp = conn.getresponse()
    body = json.loads(resp.read())
    conn.close()
    print(f"  Submit status: {resp.status}")
    return body.get("report_id", "")


def poll_status(report_id: str, max_wait: int = 300) -> dict:
    """Poll until done or timeout."""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        resp = req("GET", f"/api/reports/{report_id}/status")
        status = resp.get("status")
        step   = resp.get("current_step")
        print(f"  Status: {status:<12} | Step: {step}")
        if status in ("completed", "failed"):
            return resp
        time.sleep(5)
    return {}


# ─── main test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Use any available image in outputs or data
    sample_images = []
    for root, _, files in os.walk("."):
        for f in files:
            if f.lower().endswith((".jpg",".jpeg",".png")):
                sample_images.append(os.path.join(root, f))
        if sample_images:
            break

    if not sample_images:
        print("No sample image found. Please place a .jpg/.png in the project directory.")
        exit(1)

    image_path = sample_images[0]
    print(f"\nUsing image: {image_path}\n")

    # ─── Health check ─────────────────────────────────────────────────────────
    health = req("GET", "/api/health")
    print(f"Health check: {health}")

    # ─── Test SHORT report ────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("TEST 1: SHORT REPORT (3 pages)")
    print("="*60)
    rid_short = submit_analysis(image_path, "short")
    print(f"  Report ID: {rid_short}")
    result_short = poll_status(rid_short)
    print(f"  Final status: {result_short.get('status')}")

    # ─── Test LONG report ─────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("TEST 2: LONG REPORT (full 11 pages)")
    print("="*60)
    rid_long = submit_analysis(image_path, "long")
    print(f"  Report ID: {rid_long}")
    result_long = poll_status(rid_long)
    print(f"  Final status: {result_long.get('status')}")

    # ─── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    for label, rid, result in [("SHORT", rid_short, result_short), ("LONG", rid_long, result_long)]:
        st = result.get("status", "unknown")
        errors = result.get("errors", [])
        print(f"  {label} report ({rid}): {st}" + (f" — ERRORS: {errors}" if errors else " ✓"))

    # Check reports list
    reports = req("GET", "/api/reports")
    print(f"\nTotal reports in system: {reports.get('total', 0)}")
    for r in reports.get("reports", []):
        print(f"  [{r.get('report_id')}] status={r.get('status')} pdf={r.get('pdf_available')}")
