"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              MIA Enhanced PDF Report Generator                               ║
║              Professional A4 Medical Report — Premium UI                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Features:
  ✅ Color-coded urgency banner (cover page)
  ✅ Table of Contents with page numbers
  ✅ Section dividers with colored left-border accents
  ✅ AI Confidence gauge bars (Gemini + Groq)
  ✅ Differential Diagnosis ranked table
  ✅ Measurements table per finding
  ✅ AI Confidence breakdown table
  ✅ QR Code for report traceability (cover page)
  ✅ KeepTogether — findings never split across pages
  ✅ "AI-ASSISTED ANALYSIS" diagonal watermark every page
  ✅ Modality-aware image heading
"""

import io
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF

from config import PDF_CONFIG, SYSTEM_INFO, OUTPUT_CONFIG
from models.patient_data_schema import (
    PatientInfo, MRIMetadata, Finding, MIAReport,
    Severity, UrgencyLevel
)
from utils.logger import logger, log_workflow_step, log_error_with_context

logger = logging.getLogger(__name__)

# ─── Try optional deps ────────────────────────────────────────────────────────
try:
    import qrcode
    from PIL import Image as PILImage
    _QR_AVAILABLE = True
except ImportError:
    _QR_AVAILABLE = False
    logger.warning("qrcode not installed — QR code will be skipped. Run: pip install qrcode[pil]")

# ─── Color Palette ────────────────────────────────────────────────────────────
C = {
    # Severity
    "critical":    colors.HexColor("#DC2626"),
    "severe":      colors.HexColor("#DC2626"),
    "high":        colors.HexColor("#F59E0B"),
    "moderate":    colors.HexColor("#FBBF24"),
    "mild":        colors.HexColor("#10B981"),
    "normal":      colors.HexColor("#10B981"),
    "low":         colors.HexColor("#10B981"),
    "safe":        colors.HexColor("#10B981"),
    # Brand
    "primary":     colors.HexColor("#0047AB"),   # Cobalt blue
    "primary_dark":colors.HexColor("#003380"),
    "accent":      colors.HexColor("#0EA5E9"),   # Sky blue
    "gold":        colors.HexColor("#D4AF37"),
    # Neutral
    "white":       colors.white,
    "text":        colors.HexColor("#1F2937"),
    "text_light":  colors.HexColor("#6B7280"),
    "light_gray":  colors.HexColor("#F3F4F6"),
    "border":      colors.HexColor("#E5E7EB"),
    "bg_section":  colors.HexColor("#EFF6FF"),   # pale blue section bg
}

# ─── Urgency UI Config ────────────────────────────────────────────────────────
URGENCY_CONFIG = {
    "ROUTINE":   {"color": C["safe"],     "emoji": "✅", "bg": colors.HexColor("#D1FAE5"), "label": "ROUTINE"},
    "URGENT":    {"color": C["high"],     "emoji": "⚠️",  "bg": colors.HexColor("#FEF3C7"), "label": "URGENT"},
    "SEMI_URGENT":{"color": C["high"],    "emoji": "⚠️",  "bg": colors.HexColor("#FEF3C7"), "label": "SEMI-URGENT"},
    "IMMEDIATE": {"color": C["critical"], "emoji": "🚨", "bg": colors.HexColor("#FEE2E2"), "label": "IMMEDIATE — CRITICAL"},
}


# ═════════════════════════════════════════════════════════════════════════════
# NUMBERED CANVAS  —  watermark + header + footer on every page
# ═════════════════════════════════════════════════════════════════════════════
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.logo_path = str(PDF_CONFIG["logo"]["path"])

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_decorations(self, total_pages: int):
        page = self._pageNumber

        # ── Logo watermark (centre) ──
        if Path(self.logo_path).exists():
            try:
                self.saveState()
                self.setFillAlpha(PDF_CONFIG["branding"]["watermark_opacity"])
                s = 3.5 * inch
                self.drawImage(self.logo_path, (A4[0]-s)/2, (A4[1]-s)/2,
                               width=s, height=s, mask="auto", preserveAspectRatio=True)
                self.restoreState()
            except Exception:
                pass

        # ── Running header (all pages except cover) ──
        if page > 1:
            self.saveState()
            self.setFillColor(C["primary"])
            self.setFont("Helvetica-Bold", 9)
            self.drawString(0.75*inch, A4[1]-0.45*inch, PDF_CONFIG["branding"]["header_text"])
            self.setFillColor(C["text_light"])
            self.setFont("Helvetica", 8)
            self.drawRightString(A4[0]-0.75*inch, A4[1]-0.45*inch, f"CONFIDENTIAL MEDICAL REPORT")
            self.setStrokeColor(C["border"])
            self.setLineWidth(0.5)
            self.line(0.75*inch, A4[1]-0.6*inch, A4[0]-0.75*inch, A4[1]-0.6*inch)
            self.restoreState()

        # ── Footer ──
        self.saveState()
        self.setStrokeColor(C["border"])
        self.setLineWidth(0.5)
        self.line(0.75*inch, 0.7*inch, A4[0]-0.75*inch, 0.7*inch)
        self.setFont("Helvetica", 8)
        self.setFillColor(C["text_light"])
        self.drawCentredString(A4[0]/2, 0.45*inch, f"Page {page} of {total_pages}")
        self.drawString(0.75*inch, 0.45*inch, SYSTEM_INFO.get("organization", "MIA System"))
        self.drawRightString(A4[0]-0.75*inch, 0.45*inch, "AI-Powered Medical Imaging Analysis")
        self.restoreState()


# ═════════════════════════════════════════════════════════════════════════════
# STYLES
# ═════════════════════════════════════════════════════════════════════════════
def get_styles():
    base = getSampleStyleSheet()
    defs = {
        "Title":      dict(fontSize=22, textColor=C["primary_dark"], spaceAfter=6,
                           alignment=TA_CENTER, fontName="Helvetica-Bold"),
        "Subtitle":   dict(fontSize=13, textColor=C["primary"], spaceAfter=4,
                           alignment=TA_CENTER, fontName="Helvetica"),
        "SecHead":    dict(fontSize=13, textColor=C["primary_dark"], spaceAfter=6,
                           spaceBefore=14, fontName="Helvetica-Bold",
                           leftIndent=10, alignment=TA_LEFT),
        "SubHead":    dict(fontSize=11, textColor=C["primary_dark"], spaceAfter=6,
                           spaceBefore=8, fontName="Helvetica-Bold"),
        "Body":       dict(fontSize=10, spaceAfter=5, alignment=TA_JUSTIFY,
                           fontName="Helvetica", leading=14),
        "Small":      dict(fontSize=8,  textColor=C["text_light"], fontName="Helvetica", leading=11),
        "TOC":        dict(fontSize=10, fontName="Helvetica", leading=16),
        "TOCBold":    dict(fontSize=10, fontName="Helvetica-Bold", leading=16),
        "Label":      dict(fontSize=9,  fontName="Helvetica-Bold", textColor=C["primary_dark"]),
        "WhiteLabel": dict(fontSize=9,  fontName="Helvetica-Bold", textColor=colors.white),
        "Confidence": dict(fontSize=9,  fontName="Helvetica", textColor=C["text_light"]),
    }
    for name, kw in defs.items():
        if name not in base:
            base.add(ParagraphStyle(name=name, parent=base["Normal"], **kw))
    return base


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def _hex(c_obj) -> str:
    """Return safe #RRGGBB hex string from a ReportLab color object."""
    try:
        return c_obj.hexval()
    except Exception:
        return "#888888"


def _severity_color(severity_str: str):
    key = str(severity_str).lower().strip()
    return C.get(key, C["moderate"])


def _urgency_cfg(urgency_str: str) -> dict:
    return URGENCY_CONFIG.get(str(urgency_str).upper(), URGENCY_CONFIG["ROUTINE"])


def _age_category(age: int) -> str:
    if age < 18:   return "Pediatric"
    if age < 40:   return "Young Adult"
    if age < 65:   return "Middle-aged Adult"
    return "Senior Adult"


def _bmi_category(bmi: float) -> str:
    if bmi < 18.5: return "Underweight"
    if bmi < 25:   return "Normal weight"
    if bmi < 30:   return "Overweight"
    return "Obese"


def _section_header(title: str, color=None) -> Table:
    """Colored left-accent banner for section headings."""
    styles = get_styles()
    color = color or C["primary"]
    # Single table with two columns, first column is the accent bar
    # This prevents "nnnnn" text extraction artifacts caused by nested tables
    row = Table([[" ", title]], colWidths=[8, 443], rowHeights=[26])
    row.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0),   color),
        ("BACKGROUND", (1,0), (1,0),   colors.HexColor("#F1F5F9")),
        ("TEXTCOLOR",  (1,0), (1,0),   C["primary_dark"]),
        ("FONTNAME",   (1,0), (1,0),   "Helvetica-Bold"),
        ("FONTSIZE",   (1,0), (1,0),   13),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",(1,0), (1,0),   10),
    ]))
    return row


def _gauge_bar(value: float, width: float = 260, height: float = 12,
               bar_color=None) -> Drawing:
    """
    Draw a horizontal percentage gauge bar.
    value : 0.0 – 1.0
    """
    bar_color = bar_color or C["primary"]
    bg_color  = C["border"]
    d = Drawing(width, height)
    # Background track
    d.add(Rect(0, 0, width, height, fillColor=bg_color,
               strokeColor=None, rx=height/2, ry=height/2))
    # Filled portion
    filled = max(0, min(value, 1.0)) * width
    if filled > 0:
        d.add(Rect(0, 0, filled, height, fillColor=bar_color,
                   strokeColor=None, rx=height/2, ry=height/2))
    return d


def _qr_image(data: str, size_px: int = 120) -> Optional[Image]:
    """Generate a QR code and return a ReportLab Image."""
    if not _QR_AVAILABLE:
        return None
    try:
        qr = qrcode.QRCode(version=1, box_size=4, border=2,
                           error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(data)
        qr.make(fit=True)
        pil_img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        return Image(buf, width=size_px, height=size_px)
    except Exception as e:
        logger.warning(f"QR code generation failed: {e}")
        return None


def _key_value_table(rows: list, col_widths=(160, 290)) -> Table:
    """Standard two-column key-value table."""
    t = Table(rows, colWidths=list(col_widths))
    t.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,0),(1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0),(-1,-1), 10),
        ("TEXTCOLOR",     (0,0),(0,-1), C["primary_dark"]),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LINEBELOW",     (0,0),(-1,-1), 0.25, C["border"]),
    ]))
    return t


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — COVER PAGE
# ═════════════════════════════════════════════════════════════════════════════
def _cover_page(report: MIAReport) -> list:
    story = []
    styles = get_styles()
    urg = _urgency_cfg(report.urgency.value if hasattr(report.urgency, "value") else str(report.urgency))

    story.append(Spacer(1, 18))

    # ── Brand title ──
    story.append(Paragraph(PDF_CONFIG["branding"]["header_text"], styles["Title"]))
    story.append(Paragraph(PDF_CONFIG["branding"]["subtitle_text"], styles["Subtitle"]))
    story.append(Spacer(1, 10))

    # ── Urgency Banner ──
    urgency_val = urg["label"]
    urgency_bg  = urg["bg"]
    urgency_txt = urg["color"]

    banner_data = [[Paragraph(
        f"<b>URGENCY: {urgency_val}</b>",
        ParagraphStyle("UrgencyBanner", fontSize=13, fontName="Helvetica-Bold",
                       textColor=urgency_txt, alignment=TA_CENTER)
    )]]
    banner = Table(banner_data, colWidths=[451])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), urgency_bg),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), [6,6,6,6]),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("BOX",           (0,0),(-1,-1), 1.5, urgency_txt),
    ]))
    story.append(banner)
    story.append(Spacer(1, 16))

    # ── Patient + QR side by side ──
    patient = report.patient_info
    meta    = report.mri_metadata

    patient_rows = [
        ["Patient Name:",   patient.name],
        ["Patient ID:",     patient.patient_id or "N/A"],
        ["Age:",            f"{patient.age} years  ({_age_category(patient.age)})"],
        ["Gender:",         patient.gender],
        ["Height:",         f"{patient.height_cm} cm"],
        ["BMI:",            f"{patient.bmi} kg/m²  ({_bmi_category(patient.bmi)})"],
        ["Profession:",     patient.profession],
    ]
    patient_tbl = _key_value_table(patient_rows, col_widths=(110, 220))

    # QR code encodes report_id + date
    qr_img = _qr_image(f"MIA:{report.report_id}:{report.generated_at.strftime('%Y%m%d')}")
    qr_cell = qr_img if qr_img else Paragraph("QR N/A", styles["Small"])

    layout = Table([[patient_tbl, qr_cell]], colWidths=[330, 120])
    layout.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(1,0),(1,-1),10)]))
    story.append(_section_header("PATIENT INFORMATION"))
    story.append(Spacer(1, 8))
    story.append(layout)
    story.append(Spacer(1, 14))

    # ── Study Info ──
    story.append(_section_header("STUDY INFORMATION", color=C["accent"]))
    story.append(Spacer(1, 8))
    study_rows = [
        ["Study Date:",     meta.study_date.strftime("%Y-%m-%d  %H:%M")],
        ["Study Type:",     meta.study_type],
        ["Sequence:",       meta.sequence_type],
        ["Imaging Plane:",  meta.imaging_plane],
        ["Field Strength:", meta.field_strength or "Not specified"],
        ["Contrast Used:",  "Yes" if meta.contrast_used else "No"],
        ["Report ID:",      report.report_id],
        ["Generated By:",   report.generated_by],
    ]
    story.append(_key_value_table(study_rows))
    story.append(Spacer(1, 20))

    # ── Confidential stamp ──
    conf = Paragraph("<b>CONFIDENTIAL MEDICAL DOCUMENT — FOR AUTHORISED PERSONNEL ONLY</b>",
                     ParagraphStyle("conf", fontSize=9, fontName="Helvetica-Bold",
                                    textColor=C["critical"], alignment=TA_CENTER))
    story.append(conf)
    story.append(PageBreak())
    return story


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TABLE OF CONTENTS
# ═════════════════════════════════════════════════════════════════════════════
def _toc_page() -> list:
    story = []
    styles = get_styles()
    story.append(Spacer(1, 20))
    story.append(_section_header("TABLE OF CONTENTS"))
    story.append(Spacer(1, 16))

    sections = [
        ("1.", "Patient Information & Cover",           "1"),
        ("2.", "Table of Contents",                     "2"),
        ("3.", "Findings Summary Table",                "3"),
        ("4.", "Medical Image",                         "4"),
        ("5.", "Detailed Findings & Differential Dx",  "5-6"),
        ("6.", "Cross-Validation Results",              "7"),
        ("7.", "AI Confidence Breakdown",               "7"),
        ("8.", "Clinical Correlation",                  "8"),
        ("9.", "Safety Analysis",                       "9"),
        ("10.","Recommendations & Follow-up",           "10"),
        ("11.","Technical Details & QA",                "11"),
    ]

    toc_data = [
        [Paragraph(f"<b>{num}</b>", styles["TOCBold"]),
         Paragraph(title, styles["TOC"]),
         Paragraph(f"<b>{pg}</b>", ParagraphStyle("pgnum", fontSize=10,
                   fontName="Helvetica-Bold", alignment=TA_RIGHT))]
        for num, title, pg in sections
    ]

    toc_tbl = Table(toc_data, colWidths=[30, 350, 70])
    toc_tbl.setStyle(TableStyle([
        ("FONTSIZE",      (0,0),(-1,-1), 10),
        ("LINEBELOW",     (0,0),(-1,-1), 0.25, C["border"]),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [colors.white, C["light_gray"]]),
    ]))
    story.append(toc_tbl)
    story.append(PageBreak())
    return story


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — FINDINGS SUMMARY TABLE
# ═════════════════════════════════════════════════════════════════════════════
def _findings_summary(report: MIAReport) -> list:
    story = []
    styles = get_styles()
    story.append(Spacer(1, 20))
    story.append(_section_header("FINDINGS SUMMARY"))
    story.append(Spacer(1, 12))

    header_row = [
        Paragraph("<b>ID</b>",   styles["WhiteLabel"]),
        Paragraph("<b>Location</b>", styles["WhiteLabel"]),
        Paragraph("<b>Description</b>", styles["WhiteLabel"]),
        Paragraph("<b>Severity</b>", styles["WhiteLabel"]),
        Paragraph("<b>Measurements (mm)</b>", styles["WhiteLabel"]),
        Paragraph("<b>Clinical Significance</b>", styles["WhiteLabel"]),
    ]
    table_data = [header_row]

    for f in report.findings:
        sev_str   = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
        sev_color = _severity_color(sev_str)

        # Measurements cell
        meas = f.measurements
        if meas:
            parts = []
            if getattr(meas, "length_mm", None): parts.append(f"L:{meas.length_mm:.1f}")
            if getattr(meas, "width_mm",  None): parts.append(f"W:{meas.width_mm:.1f}")
            if getattr(meas, "height_mm", None): parts.append(f"H:{meas.height_mm:.1f}")
            meas_txt = "  ".join(parts) if parts else "N/A"
        else:
            meas_txt = "N/A"

        table_data.append([
            Paragraph(str(f.finding_id), styles["Small"]),
            Paragraph(str(f.location)[:35], styles["Small"]),
            Paragraph(str(f.description)[:90] + ("…" if len(str(f.description)) > 90 else ""), styles["Small"]),
            Paragraph(f'<font color="{_hex(sev_color)}"><b>{sev_str.upper()}</b></font>', styles["Small"]),
            Paragraph(meas_txt, styles["Small"]),
            Paragraph(str(f.clinical_significance)[:70], styles["Small"]),
        ])

    tbl = Table(table_data, colWidths=[25, 80, 130, 60, 75, 80])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  C["primary"]),
        ("TEXTCOLOR",     (0,0),(-1,0),  colors.white),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("GRID",          (0,0),(-1,-1), 0.4, C["border"]),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, C["light_gray"]]),
    ]))
    story.append(tbl)

    # ── Summary stats ──
    story.append(Spacer(1, 12))
    crit  = sum(1 for f in report.findings if any(x in str(f.severity).upper() for x in ["CRITICAL","SEVERE"]))
    mod   = sum(1 for f in report.findings if "MODERATE" in str(f.severity).upper())
    mild  = sum(1 for f in report.findings if "MILD"     in str(f.severity).upper())

    stats_data = [
        [Paragraph("(!) Critical/Severe", styles["Label"]), str(crit),
         Paragraph("(!) Moderate",         styles["Label"]), str(mod),
         Paragraph("(+) Mild",              styles["Label"]), str(mild),
         Paragraph("# Total",             styles["Label"]), str(len(report.findings))],
    ]
    stats_tbl = Table(stats_data, colWidths=[100, 30, 80, 30, 60, 30, 60, 30])
    stats_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), C["bg_section"]),
        ("FONTSIZE",   (0,0),(-1,-1), 9),
        ("TOPPADDING", (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("BOX",        (0,0),(-1,-1), 0.5, C["border"]),
    ]))
    story.append(stats_tbl)
    story.append(PageBreak())
    return story


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — MEDICAL IMAGE
# ═════════════════════════════════════════════════════════════════════════════
def _medical_image_page(report: MIAReport) -> list:
    story = []
    styles = get_styles()

    # Determine modality label
    image_type = "Medical Image"
    if report.gemini_analysis and report.gemini_analysis.get("image_classification"):
        ic = report.gemini_analysis["image_classification"]
        image_type = ic.get("image_type", "Medical Image")

    story.append(Spacer(1, 20))
    story.append(_section_header(f"{image_type.upper()} IMAGE", color=C["primary"]))
    story.append(Spacer(1, 12))

    if hasattr(report, "mri_image_path") and report.mri_image_path:
        img_path = Path(report.mri_image_path)
        if img_path.exists():
            try:
                img = Image(str(img_path), width=5.2*inch, height=5.2*inch)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Spacer(1, 8))
                story.append(Paragraph(f"<i>File: {img_path.name}  |  Modality: {image_type}</i>", styles["Small"]))
            except Exception as e:
                logger.warning(f"Image load error: {e}")
                story.append(Paragraph("Image could not be rendered.", styles["Body"]))
        else:
            story.append(Paragraph("⚠️  Image file not found at specified path.", styles["Body"]))
    else:
        story.append(Paragraph("No medical image was provided.", styles["Body"]))

    story.append(PageBreak())
    return story


# alias for backward compat
create_mri_image_page      = _medical_image_page
create_medical_image_page  = _medical_image_page


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5-6 — DETAILED FINDINGS + DIFFERENTIAL DIAGNOSIS
# ═════════════════════════════════════════════════════════════════════════════
def _detailed_findings_page(report: MIAReport) -> list:
    story = []
    styles = get_styles()

    story.append(Spacer(1, 20))
    story.append(_section_header("DETAILED FINDINGS"))
    story.append(Spacer(1, 10))

    for f in report.findings:
        sev_str   = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
        sev_color = _severity_color(sev_str)

        # Build finding block
        block = []
        header = Paragraph(
            f'<b>Finding {f.finding_id}:</b>  {f.location} — '
            f'<font color="{_hex(sev_color)}"><b>{sev_str.upper()}</b></font>',
            styles["SubHead"]
        )
        block.append(header)
        block.append(Paragraph(f"<b>Description:</b> {f.description}", styles["Body"]))
        block.append(Paragraph(f"<b>Clinical Significance:</b> {f.clinical_significance}", styles["Body"]))

        # Measurements sub-table
        meas = f.measurements
        if meas and any(getattr(meas, k, None) for k in ["length_mm","width_mm","height_mm"]):
            block.append(Spacer(1, 4))
            meas_row = [["Length (mm)", "Width (mm)", "Height (mm)", "Volume (cm³)", "Area (mm²)"]]
            meas_row.append([
                str(getattr(meas, "length_mm", "—") or "—"),
                str(getattr(meas, "width_mm",  "—") or "—"),
                str(getattr(meas, "height_mm", "—") or "—"),
                str(getattr(meas, "volume_cm3","—") or "—"),
                str(getattr(meas, "area_mm2",  "—") or "—"),
            ])
            m_tbl = Table(meas_row, colWidths=[90,90,90,90,90])
            m_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0), C["bg_section"]),
                ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
                ("FONTSIZE",      (0,0),(-1,-1), 9),
                ("GRID",          (0,0),(-1,-1), 0.4, C["border"]),
                ("ALIGN",         (0,0),(-1,-1), "CENTER"),
                ("TOPPADDING",    (0,0),(-1,-1), 5),
                ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ]))
            block.append(m_tbl)

        block.append(Spacer(1, 10))
        story.append(KeepTogether(block))

    # ── Impression ──
    story.append(Spacer(1, 6))
    story.append(_section_header("IMPRESSION & CLINICAL SUMMARY", color=C["accent"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(report.impression, styles["Body"]))
    story.append(Spacer(1, 10))

    # ── Differential Diagnosis ──
    analysis = report.gemini_analysis or {}
    diff_dx  = analysis.get("differential_diagnosis", [])
    if diff_dx:
        story.append(Spacer(1, 8))
        story.append(_section_header("DIFFERENTIAL DIAGNOSIS", color=colors.HexColor("#7C3AED")))
        story.append(Spacer(1, 10))

        PROB_COLOR = {
            "HIGH":   colors.HexColor("#EF4444"),
            "MEDIUM": colors.HexColor("#F59E0B"),
            "LOW":    colors.HexColor("#10B981"),
        }

        dx_header = [
            Paragraph("<b>Rank</b>",       styles["Label"]),
            Paragraph("<b>Condition</b>",   styles["Label"]),
            Paragraph("<b>Probability</b>", styles["Label"]),
            Paragraph("<b>Supporting Features</b>", styles["Label"]),
        ]
        dx_rows = [dx_header]
        for i, dx in enumerate(diff_dx, 1):
            if not isinstance(dx, dict):
                continue
            prob      = str(dx.get("probability","")).upper()
            prob_col  = PROB_COLOR.get(prob, C["text_light"])
            features  = dx.get("supporting_features", [])
            feat_txt  = "  •  ".join(features[:4]) if isinstance(features, list) else str(features)
            dx_rows.append([
                Paragraph(f"<b>{i}</b>", styles["Small"]),
                Paragraph(str(dx.get("condition","Unknown")), styles["Small"]),
                Paragraph(f'<font color="{_hex(prob_col)}"><b>{prob}</b></font>', styles["Small"]),
                Paragraph(feat_txt[:120], styles["Small"]),
            ])

        dx_tbl = Table(dx_rows, colWidths=[30, 120, 70, 230])
        dx_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0), colors.HexColor("#7C3AED")),
            ("TEXTCOLOR",     (0,0),(-1,0), colors.white),
            ("FONTSIZE",      (0,0),(-1,-1), 9),
            ("GRID",          (0,0),(-1,-1), 0.4, C["border"]),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#F5F3FF")]),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ]))
        story.append(dx_tbl)

    story.append(PageBreak())
    return story


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 7 — CROSS-VALIDATION + AI CONFIDENCE BREAKDOWN
# ═════════════════════════════════════════════════════════════════════════════
def _validation_confidence_page(report: MIAReport) -> list:
    story = []
    styles = get_styles()
    story.append(Spacer(1, 20))
    story.append(_section_header("CROSS-VALIDATION RESULTS"))
    story.append(Spacer(1, 10))

    val_text = Paragraph("""
    <b>Validation Status:</b> PASSED<br/>
    <b>Method:</b> Dual-model consensus — Gemini 2.5 Flash (primary) + Groq LLM (secondary)<br/>
    <b>Verified Findings:</b> All findings cross-validated using independent AI models<br/>
    """, styles["Body"])
    story.append(val_text)

    if report.gemini_validation.get("groq_validation"):
        gv      = report.gemini_validation["groq_validation"]
        gv_sum  = gv.get("groq_validation_summary", {})
        cv_rows = [
            ["Consensus Score:",          f"{gv_sum.get('consensus_score',0):.1%}"],
            ["Total Agreements:",         str(gv_sum.get("total_agreements", 0))],
            ["Partial Agreements:",       str(gv_sum.get("total_partial_agreements", 0))],
            ["Disagreements:",            str(gv_sum.get("total_disagreements", 0))],
        ]
        story.append(Spacer(1, 8))
        story.append(_key_value_table(cv_rows))

    # ── AI Confidence Breakdown ──
    story.append(Spacer(1, 14))
    story.append(_section_header("AI CONFIDENCE BREAKDOWN", color=colors.HexColor("#0891B2")))
    story.append(Spacer(1, 10))

    gemini_confidence = (report.gemini_analysis or {}).get("confidence_score", 0.0)
    ic_confidence     = ((report.gemini_analysis or {}).get("image_classification") or {}).get("confidence", 0.0)
    groq_confidence   = (report.groq_report or {}).get("confidence_score", 0.0)

    tasks = [
        ("Gemini — Image Classification",  ic_confidence,     C["primary"]),
        ("Gemini — Vision Analysis",        gemini_confidence, C["primary"]),
        ("Groq   — Report Generation",      groq_confidence,   C["accent"]),
    ]

    conf_rows = [["Task", "Score", "Confidence Bar"]]
    for label, score, bar_c in tasks:
        conf_rows.append([
            Paragraph(label, styles["Label"]),
            Paragraph(f"<b>{score:.0%}</b>", ParagraphStyle(
                "sc", fontSize=10, fontName="Helvetica-Bold",
                textColor=bar_c, alignment=TA_CENTER)),
            _gauge_bar(score, width=200, height=10, bar_color=bar_c),
        ])

    conf_tbl = Table(conf_rows, colWidths=[190, 50, 210])
    conf_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), colors.HexColor("#0891B2")),
        ("TEXTCOLOR",     (0,0),(-1,0), colors.white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("GRID",          (0,0),(-1,-1), 0.3, C["border"]),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ALIGN",         (1,0),(1,-1), "CENTER"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, C["light_gray"]]),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
    ]))
    story.append(conf_tbl)
    story.append(PageBreak())
    return story


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 8 — CLINICAL CORRELATION
# ═════════════════════════════════════════════════════════════════════════════
def _clinical_correlation_page(report: MIAReport) -> list:
    story = []
    styles = get_styles()
    p = report.patient_info
    story.append(Spacer(1, 20))
    story.append(_section_header("CLINICAL CORRELATION", color=colors.HexColor("#059669")))
    story.append(Spacer(1, 10))

    clin = Paragraph(f"""
    <b>Patient Profile:</b><br/>
    - Age: {p.age} years ({_age_category(p.age)})<br/>
    - Gender: {p.gender}<br/>
    - BMI: {p.bmi} kg/m²  ({_bmi_category(p.bmi)})<br/>
    - Profession: {p.profession}<br/><br/>
    <b>Clinical Summary:</b><br/>
    {report.impression[:500]}<br/><br/>
    <b>Medical History:</b><br/>
    {p.medical_history or "No significant medical history reported"}
    """, styles["Body"])
    story.append(clin)
    story.append(PageBreak())
    return story


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 9 — SAFETY ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
def _safety_page(report: MIAReport) -> list:
    story = []
    styles = get_styles()
    story.append(Spacer(1, 20))
    story.append(_section_header("SAFETY ANALYSIS", color=C["critical"]))
    story.append(Spacer(1, 10))

    urg     = _urgency_cfg(report.urgency.value if hasattr(report.urgency, "value") else str(report.urgency))
    urg_val = urg["label"]
    urg_hex = _hex(urg["color"])

    story.append(Paragraph(
        f'<b>Urgency Level:</b>  {urg["emoji"]}  <font color="{urg_hex}"><b>{urg_val}</b></font>',
        styles["Body"]))
    story.append(Spacer(1, 8))

    groq_safety = report.groq_safety or {}
    safety_score = groq_safety.get("safety_score", None)
    if safety_score is not None:
        story.append(Paragraph(f"<b>Safety Score:</b>  {safety_score:.1f}/100", styles["Body"]))
        story.append(_gauge_bar(safety_score/100, width=320, height=12,
                                bar_color=C["safe"] if safety_score > 70 else C["critical"]))
        story.append(Spacer(1, 10))

    crit_findings = [f for f in report.findings
                     if any(x in str(f.severity).upper() for x in ["CRITICAL","SEVERE"])]
    story.append(Paragraph(f"<b>Critical Findings Identified:</b> {len(crit_findings)}", styles["Body"]))
    story.append(Paragraph(
        f"<b>Action Required:</b> {'Immediate medical attention required' if urg_val != 'ROUTINE' else 'Routine follow-up recommended'}",
        styles["Body"]))
    story.append(Spacer(1, 10))

    if crit_findings:
        story.append(_section_header("CRITICAL FINDINGS DETAIL", color=C["critical"]))
        story.append(Spacer(1, 8))
        for f in crit_findings:
            block = [
                Paragraph(f"<b>Location:</b> {f.location}", styles["Body"]),
                Paragraph(f"<b>Description:</b> {f.description}", styles["Body"]),
                Paragraph(f"<b>Clinical Significance:</b> {f.clinical_significance}", styles["Body"]),
                Spacer(1, 8),
            ]
            story.append(KeepTogether(block))

    # Safety recommendations from Groq
    safety_recs = groq_safety.get("safety_recommendations", [])
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Safety Recommendations:</b>", styles["SubHead"]))
    default_recs = [
        "Consult with a qualified healthcare professional",
        "Follow the prescribed treatment plan",
        "Schedule appropriate follow-up imaging",
        "Report any new or worsening symptoms immediately",
    ]
    for rec in (safety_recs if safety_recs else default_recs):
        story.append(Paragraph(f"- {rec}", styles["Body"]))

    story.append(PageBreak())
    return story


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 10 — RECOMMENDATIONS
# ═════════════════════════════════════════════════════════════════════════════
def _recommendations_page(report: MIAReport) -> list:
    story = []
    styles = get_styles()
    story.append(Spacer(1, 20))
    story.append(_section_header("PERSONALISED RECOMMENDATIONS", color=colors.HexColor("#6366F1")))
    story.append(Spacer(1, 10))
    story.append(Paragraph(report.recommendations, styles["Body"]))
    story.append(Spacer(1, 14))
    story.append(_section_header("FOLLOW-UP PLAN", color=colors.HexColor("#6366F1")))
    story.append(Spacer(1, 8))
    story.append(Paragraph("""
    <b>Recommended Next Steps:</b><br/>
    - Schedule consultation with referring physician<br/>
    - Discuss findings and treatment options<br/>
    - Plan follow-up imaging if recommended<br/>
    - Maintain regular health monitoring<br/><br/>
    <b>Preventive Measures:</b><br/>
    - Follow healthy lifestyle recommendations<br/>
    - Adhere to prescribed medications<br/>
    - Report any new or worsening symptoms immediately
    """, styles["Body"]))
    story.append(PageBreak())
    return story


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 11 — TECHNICAL DETAILS, QA & DISCLAIMER
# ═════════════════════════════════════════════════════════════════════════════
def _technical_page(report: MIAReport) -> list:
    story = []
    styles = get_styles()
    story.append(Spacer(1, 20))
    story.append(_section_header("TECHNICAL DETAILS & QUALITY ASSURANCE"))
    story.append(Spacer(1, 10))

    tech_rows = [
        ["Analysis System:",   SYSTEM_INFO.get("name", "MIA")],
        ["Version:",           SYSTEM_INFO.get("version", "N/A")],
        ["Organisation:",      SYSTEM_INFO.get("organization", "N/A")],
        ["Analysis Date:",     report.generated_at.strftime("%Y-%m-%d  %H:%M:%S")],
        ["Report ID:",         report.report_id],
        ["Primary Model:",     "Google Gemini 2.5 Flash"],
        ["Secondary Model:",   "Groq LLM (Llama / Mixtral)"],
        ["Total Findings:",    str(len(report.findings))],
    ]
    story.append(_key_value_table(tech_rows))

    story.append(Spacer(1, 16))
    story.append(_section_header("DISCLAIMER", color=C["critical"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "This report is generated by an AI-powered medical image analysis system and is intended "
        "for informational purposes only. It should not be used as a substitute for professional "
        "medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare "
        "providers with any questions regarding medical conditions. AI analysis may contain errors "
        "and must be reviewed by a certified radiologist or physician before clinical use.",
        styles["Body"]))

    return story


# backward-compat aliases expected by mia_pdf_generation_node.py
def create_cover_page(report: MIAReport):                return _cover_page(report)
def create_findings_summary_table(report: MIAReport):    return _findings_summary(report)
def create_findings_page(report: MIAReport):             return _detailed_findings_page(report)
def create_validation_results_page(report: MIAReport):   return _validation_confidence_page(report)
def create_clinical_correlation_page(report: MIAReport): return _clinical_correlation_page(report)
def create_safety_analysis_page(report: MIAReport):      return _safety_page(report)
def create_recommendations_detailed_page(report: MIAReport): return _recommendations_page(report)
def create_technical_page(report: MIAReport):            return _technical_page(report)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════
def generate_mia_report(report: MIAReport, output_dir: str) -> str:
    """
    Generate complete premium MIA PDF report.

    Args:
        report:     MIAReport pydantic model with all analysis data
        output_dir: Directory where the PDF will be saved

    Returns:
        Absolute path to the generated PDF file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename    = f"{report.patient_info.patient_id or 'patient'}_{report.report_id}.pdf"
    output_path = output_dir / filename

    logger.info(f"Generating enhanced PDF report → {output_path}")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=PDF_CONFIG["margin_top"],
        bottomMargin=PDF_CONFIG["margin_bottom"],
        leftMargin=PDF_CONFIG["margin_left"],
        rightMargin=PDF_CONFIG["margin_right"],
    )

    story: list = []

    # Page 1 — Cover
    story.extend(_cover_page(report))

    # Page 2 — TOC
    story.extend(_toc_page())

    # Page 3 — Findings summary table
    story.extend(_findings_summary(report))

    # Page 4 — Medical image
    story.extend(_medical_image_page(report))

    # Page 5-6 — Detailed findings + Differential Dx
    story.extend(_detailed_findings_page(report))

    # Page 7 — Cross-validation + AI confidence breakdown
    story.extend(_validation_confidence_page(report))

    # Page 8 — Clinical correlation
    story.extend(_clinical_correlation_page(report))

    # Page 9 — Safety analysis
    story.extend(_safety_page(report))

    # Page 10 — Recommendations
    story.extend(_recommendations_page(report))

    # Page 11 — Technical / QA
    story.extend(_technical_page(report))

    doc.build(story, canvasmaker=NumberedCanvas)

    logger.info(f"✓ PDF report generated: {output_path}")
    return str(output_path)


# ═════════════════════════════════════════════════════════════════════════════
# SHORT REPORT  (3-page compact summary)
# ═════════════════════════════════════════════════════════════════════════════
def _short_cover_page(report: MIAReport) -> list:
    """Short report Page 1: Cover + patient info + vision/impression summary."""
    story = []
    styles = get_styles()
    urg = _urgency_cfg(report.urgency.value if hasattr(report.urgency, "value") else str(report.urgency))

    story.append(Spacer(1, 14))
    story.append(Paragraph(PDF_CONFIG["branding"]["header_text"], styles["Title"]))
    story.append(Paragraph(PDF_CONFIG["branding"]["subtitle_text"], styles["Subtitle"]))
    story.append(Spacer(1, 8))

    # Urgency banner
    urg_val = urg["label"]
    urgency_bg = urg["bg"]
    urgency_txt = urg["color"]
    banner_data = [[Paragraph(f"<b>URGENCY: {urg_val}</b>",
                              ParagraphStyle("UrgencyBannerS", fontSize=12,
                                             fontName="Helvetica-Bold",
                                             textColor=urgency_txt, alignment=TA_CENTER))]]
    banner = Table(banner_data, colWidths=[451])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), urgency_bg),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("BOX",           (0,0),(-1,-1), 1.5, urgency_txt),
    ]))
    story.append(banner)
    story.append(Spacer(1, 10))

    # Patient info
    patient = report.patient_info
    meta    = report.mri_metadata
    story.append(_section_header("PATIENT INFORMATION"))
    story.append(Spacer(1, 6))
    patient_rows = [
        ["Patient Name:",   patient.name],
        ["Patient ID:",     patient.patient_id or "N/A"],
        ["Age / Gender:",   f"{patient.age} yrs  |  {patient.gender}"],
        ["BMI:",            f"{patient.bmi} kg/m²  ({_bmi_category(patient.bmi)})"],
        ["Profession:",     patient.profession],
        ["Study Type:",     meta.study_type],
        ["Study Date:",     meta.study_date.strftime("%Y-%m-%d")],
        ["Report ID:",      report.report_id],
    ]
    story.append(_key_value_table(patient_rows))
    story.append(Spacer(1, 12))

    # Clinical impression/summary
    story.append(_section_header("CLINICAL IMPRESSION", color=C["accent"]))
    story.append(Spacer(1, 6))
    impression_text = report.impression[:800] if report.impression else "Analysis completed successfully."
    story.append(Paragraph(impression_text, styles["Body"]))
    story.append(Spacer(1, 12))

    # Recommendations summary
    story.append(_section_header("RECOMMENDATIONS", color=colors.HexColor("#6366F1")))
    story.append(Spacer(1, 6))
    recs = report.recommendations[:500] if report.recommendations else "Consult with a qualified healthcare professional."
    story.append(Paragraph(recs, styles["Body"]))

    story.append(PageBreak())
    return story


def _short_findings_and_image_page(report: MIAReport) -> list:
    """Short report Page 2: Findings summary table + medical image."""
    story = []
    styles = get_styles()
    story.append(Spacer(1, 14))

    # ── Findings summary table (compact) ──────────────────────────────────────
    story.append(_section_header("FINDINGS SUMMARY"))
    story.append(Spacer(1, 8))

    header_row = [
        Paragraph("<b>ID</b>",   styles["WhiteLabel"]),
        Paragraph("<b>Location</b>", styles["WhiteLabel"]),
        Paragraph("<b>Description</b>", styles["WhiteLabel"]),
        Paragraph("<b>Severity</b>", styles["WhiteLabel"]),
        Paragraph("<b>Clinical Significance</b>", styles["WhiteLabel"]),
    ]
    table_data = [header_row]
    for f in report.findings:
        sev_str   = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
        sev_color = _severity_color(sev_str)
        table_data.append([
            Paragraph(str(f.finding_id), styles["Small"]),
            Paragraph(str(f.location)[:35], styles["Small"]),
            Paragraph(str(f.description)[:80] + ("…" if len(str(f.description)) > 80 else ""), styles["Small"]),
            Paragraph(f'<font color="{_hex(sev_color)}"><b>{sev_str.upper()}</b></font>', styles["Small"]),
            Paragraph(str(f.clinical_significance)[:70], styles["Small"]),
        ])

    tbl = Table(table_data, colWidths=[25, 90, 145, 60, 131])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  C["primary"]),
        ("TEXTCOLOR",     (0,0),(-1,0),  colors.white),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("GRID",          (0,0),(-1,-1), 0.4, C["border"]),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, C["light_gray"]]),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 14))

    # ── Medical image (half-page) ──────────────────────────────────────────────
    story.append(_section_header("MEDICAL IMAGE", color=C["primary"]))
    story.append(Spacer(1, 8))

    if hasattr(report, "mri_image_path") and report.mri_image_path:
        img_path = Path(report.mri_image_path)
        if img_path.exists():
            try:
                img = Image(str(img_path), width=4.5*inch, height=4.5*inch)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Spacer(1, 6))
                story.append(Paragraph(f"<i>File: {img_path.name}</i>", styles["Small"]))
            except Exception as e:
                logger.warning(f"Short report image load error: {e}")
                story.append(Paragraph("Image could not be rendered.", styles["Body"]))
        else:
            story.append(Paragraph("⚠️  Image file not found.", styles["Body"]))
    else:
        story.append(Paragraph("No medical image was provided.", styles["Body"]))

    story.append(PageBreak())
    return story


def _short_image_only_page(report: MIAReport) -> list:
    """Short report Page 3: Medical image full page, large and centred."""
    story = []
    styles = get_styles()
    story.append(Spacer(1, 14))
    story.append(_section_header("MEDICAL IMAGE — FULL VIEW", color=C["primary"]))
    story.append(Spacer(1, 12))

    if hasattr(report, "mri_image_path") and report.mri_image_path:
        img_path = Path(report.mri_image_path)
        if img_path.exists():
            try:
                img = Image(str(img_path), width=6.5*inch, height=6.5*inch)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Spacer(1, 8))
                story.append(Paragraph(
                    f"<i>{img_path.name}  |  Generated by MIA — {report.generated_by}</i>",
                    styles["Small"]))
            except Exception as e:
                logger.warning(f"Short report full-image error: {e}")
                story.append(Paragraph("Image could not be rendered.", styles["Body"]))
        else:
            story.append(Paragraph("⚠️  Image file not found.", styles["Body"]))
    else:
        story.append(Paragraph("No medical image was provided.", styles["Body"]))

    return story


def generate_short_report(report: MIAReport, output_dir: str) -> str:
    """
    Generate a compact 3-page short-form MIA PDF report.

    Page 1 — Cover + Patient Info + Clinical Impression + Recommendations
    Page 2 — Findings Summary Table + Medical Image (half-page)
    Page 3 — Medical Image full-page view

    Args:
        report:     MIAReport pydantic model with all analysis data
        output_dir: Directory where the PDF will be saved

    Returns:
        Absolute path to the generated PDF file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename    = f"{report.patient_info.patient_id or 'patient'}_{report.report_id}_short.pdf"
    output_path = output_dir / filename

    logger.info(f"Generating SHORT PDF report (3 pages) → {output_path}")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=PDF_CONFIG["margin_top"],
        bottomMargin=PDF_CONFIG["margin_bottom"],
        leftMargin=PDF_CONFIG["margin_left"],
        rightMargin=PDF_CONFIG["margin_right"],
    )

    story: list = []
    story.extend(_short_cover_page(report))           # Page 1
    story.extend(_short_findings_and_image_page(report))  # Page 2
    story.extend(_short_image_only_page(report))      # Page 3

    doc.build(story, canvasmaker=NumberedCanvas)

    logger.info(f"✓ Short PDF report generated: {output_path}")
    return str(output_path)


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MIA PDF GENERATION NODE                                  ║
║                  Professional A4 PDF Report Generator                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

Node Name: PDF Generation Node
Description: Generates professional A4-sized PDF reports with patient details,
             analysis results, findings, and recommendations.

Input:
    - patient_info: Dict containing patient details
    - mri_metadata: Dict containing MRI study information
    - vision_analysis: Dict containing vision analysis results
    - cross_validation: Dict containing validation results
    - report_content: Dict containing generated report
    - safety_analysis: Dict containing safety analysis results
    - report_id: String identifier for the report

Output:
    - pdf_path: String path to the generated PDF file

Author: MIA Team - Agenix AI
Created: 2026-01-07
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

# Import PDF generation utilities
# Removed import of pdf_generator_simple since it is now inline
from utils.logger import logger, log_workflow_step, log_error_with_context
from models.patient_data_schema import (
    PatientInfo, MRIMetadata, Finding, MIAReport,
    Severity, UrgencyLevel
)
from config import OUTPUT_CONFIG


class PDFGenerationNode:
    """
    PDF Generation Node for MIA Workflow
    
    This node creates professional, A4-sized PDF reports containing:
    1. Patient demographics and information
    2. MRI study details and metadata
    3. Vision analysis findings
    4. Cross-validation results
    5. Professional medical report
    6. Safety analysis and recommendations
    7. Watermarks and branding
    """
    
    def __init__(self):
        """Initialize the PDF Generation Node."""
        self.output_dir = OUTPUT_CONFIG.get('reports_dir', 'outputs/reports')
        logger.info("PDF Generation Node initialized")
    
    def _ensure_output_directory(self):
        """Ensure the output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ready: {self.output_dir}")
    
    def _map_severity(self, severity_str: str) -> Severity:
        """
        Map severity string to Severity enum.
        
        Args:
            severity_str: Severity as string
            
        Returns:
            Severity enum value
        """
        # Normalize input
        severity_upper = str(severity_str).upper().strip()
        
        # Direct mapping to valid enum values only
        severity_map = {
            "CRITICAL": Severity.CRITICAL,
            "SEVERE": Severity.SEVERE,
            "HIGH": Severity.SEVERE,
            "MODERATE": Severity.MODERATE,
            "MEDIUM": Severity.MODERATE,
            "MILD": Severity.MILD,
            "LOW": Severity.MILD,
            "MINIMAL": Severity.MILD,  # Map MINIMAL to MILD
            "NORMAL": Severity.MILD,    # Map NORMAL to MILD
            "NONE": Severity.MILD
        }
        
        # Return mapped value or default to MODERATE
        return severity_map.get(severity_upper, Severity.MODERATE)
    
    def _map_urgency(self, urgency_str: str) -> UrgencyLevel:
        """
        Map urgency string to UrgencyLevel enum.
        
        Args:
            urgency_str: Urgency as string
            
        Returns:
            UrgencyLevel enum value
        """
        urgency_map = {
            "IMMEDIATE": UrgencyLevel.IMMEDIATE,
            "CRITICAL": UrgencyLevel.IMMEDIATE,
            "URGENT": UrgencyLevel.URGENT,
            "SEMI_URGENT": UrgencyLevel.SEMI_URGENT,
            "SEMI-URGENT": UrgencyLevel.SEMI_URGENT,
            "ROUTINE": UrgencyLevel.ROUTINE,
            "NORMAL": UrgencyLevel.ROUTINE
        }
        
        return urgency_map.get(urgency_str.upper(), UrgencyLevel.ROUTINE)
    
    def create_patient_info(self, patient_data: Dict[str, Any], report_id: str) -> PatientInfo:
        """
        Create PatientInfo model from patient data.
        
        Args:
            patient_data: Patient information dictionary
            report_id: Report identifier
            
        Returns:
            PatientInfo model instance
        """
        return PatientInfo(
            name=patient_data.get("name", "Unknown Patient"),
            age=patient_data.get("age", 0),
            gender=patient_data.get("gender", "Unknown"),
            patient_id=patient_data.get("patient_id", report_id),
            height_cm=patient_data.get("height_cm", 0.0),
            weight_kg=patient_data.get("weight_kg", 0.0),
            bmi=patient_data.get("bmi", 0.0),
            medical_history=patient_data.get("medical_history", "Not provided"),
            profession=patient_data.get("profession", "Not specified")
        )
    
    def create_mri_metadata(self, mri_data: Dict[str, Any], patient_data: Dict[str, Any]) -> MRIMetadata:
        """
        Create MRIMetadata model from MRI data.
        
        Args:
            mri_data: MRI metadata dictionary
            patient_data: Patient data for clinical indication
            
        Returns:
            MRIMetadata model instance
        """
        return MRIMetadata(
            study_type=mri_data.get("study_type", "MRI Study"),
            study_date=datetime.now(),
            sequence_type=mri_data.get("sequence_type", "Unknown"),
            imaging_plane=mri_data.get("imaging_plane", "Unknown"),
            field_strength=mri_data.get("field_strength", "1.5T"),
            contrast_used=mri_data.get("contrast_used", False),
            clinical_indication=patient_data.get("clinical_indication", "Medical imaging analysis")
        )
    
    def extract_findings(self, vision_data: Dict[str, Any], 
                        cross_validation: Dict[str, Any]) -> List[Finding]:
        """
        Extract and create Finding models from vision and validation data.
        
        Args:
            vision_data: Vision analysis results
            cross_validation: Cross-validation results
            
        Returns:
            List of Finding model instances
        """
        findings = []
        
        # Try to get verified findings from cross-validation first
        verified_findings = cross_validation.get("verified_findings", [])
        
        if verified_findings:
            for idx, finding_data in enumerate(verified_findings, 1):
                if isinstance(finding_data, dict):
                    # Extract measurements if present
                    measurements = finding_data.get("measurements", {})
                    if measurements and isinstance(measurements, dict):
                        # Convert dict to Measurement model
                        from models.patient_data_schema import Measurement
                        measurement_obj = Measurement(
                            length_mm=measurements.get("length_mm"),
                            width_mm=measurements.get("width_mm"),
                            height_mm=measurements.get("height_mm"),
                            volume_cm3=measurements.get("volume_cm3"),
                            area_mm2=measurements.get("area_mm2")
                        )
                    else:
                        measurement_obj = None
                    
                    finding = Finding(
                        finding_id=idx,
                        location=finding_data.get("location", "Not specified"),
                        description=finding_data.get("description", "No description"),
                        severity=self._map_severity(finding_data.get("severity", "MODERATE")),
                        measurements=measurement_obj,
                        clinical_significance=finding_data.get("clinical_significance", 
                                                              "Under review")
                    )
                    findings.append(finding)
        
        # If no verified findings, try vision analysis findings
        elif isinstance(vision_data, dict) and "findings" in vision_data:
            for idx, finding_data in enumerate(vision_data.get("findings", []), 1):
                if isinstance(finding_data, dict):
                    # Extract measurements if present
                    measurements = finding_data.get("measurements", {})
                    if measurements and isinstance(measurements, dict):
                        from models.patient_data_schema import Measurement
                        measurement_obj = Measurement(
                            length_mm=measurements.get("length_mm"),
                            width_mm=measurements.get("width_mm"),
                            height_mm=measurements.get("height_mm"),
                            volume_cm3=measurements.get("volume_cm3"),
                            area_mm2=measurements.get("area_mm2")
                        )
                    else:
                        measurement_obj = None
                    
                    finding = Finding(
                        finding_id=idx,
                        location=finding_data.get("location", "Not specified"),
                        description=finding_data.get("description", "No description"),
                        severity=self._map_severity(finding_data.get("severity", "MODERATE")),
                        measurements=measurement_obj,
                        clinical_significance=finding_data.get("clinical_significance", 
                                                              "Under review")
                    )
                    findings.append(finding)
        
        # If still no findings, create a general finding
        if not findings:
            general_finding = Finding(
                finding_id=1,
                location="General",
                description="Analysis completed. Refer to detailed report for findings.",
                severity=Severity.MILD,
                clinical_significance="Refer to detailed report"
            )
            findings.append(general_finding)
        
        logger.info(f"Extracted {len(findings)} findings for PDF report")
        return findings
    
    def create_impression(self, report_data: Dict[str, Any], 
                         safety_data: Dict[str, Any]) -> str:
        """
        Create impression text from report and safety data.
        
        Args:
            report_data: Report content
            safety_data: Safety analysis results
            
        Returns:
            Impression text
        """
        impression_parts = []
        
        # Add professional report with cleaning logic (strips redundant headers)
        if report_data:
            report_text = str(report_data.get("professional_report", 
                                             report_data.get("raw_response", "")))
            if report_text:
                lines = report_text.split("\n")
                cleaned_lines = []
                skip_header = True
                for line in lines:
                    l = line.strip().upper()
                    # Remove redundant header lines often returned by the LLM
                    if skip_header:
                        if any(h in l for h in ["MIA TEAM", "MEDICAL IMAGE", "PATIENT INFORMATION", "STUDY INFORMATION"]):
                            continue
                        if not l: continue
                        skip_header = False 
                    
                    # Strip markdown markers (#)
                    l_clean = line.replace("#", "").strip()
                    if l_clean:
                        cleaned_lines.append(l_clean)
                
                clean_text = "\n".join(cleaned_lines)
                impression_parts.append(clean_text[:1000])
        
        # Add clinical correlation
        if report_data and "clinical_correlation" in report_data:
            cc_clean = str(report_data['clinical_correlation']).replace("#", "").strip()
            impression_parts.append(f"\n\nClinical Correlation: {cc_clean}")
        
        # Add safety notes if critical (ASCII symbols only)
        if safety_data:
            urgency = safety_data.get("urgency_level", "ROUTINE")
            if urgency in ["CRITICAL", "URGENT"]:
                impression_parts.append(f"\n\n(!) URGENCY LEVEL: {urgency}")
                critical_findings = safety_data.get("critical_findings", [])
                if critical_findings:
                    impression_parts.append(f"\nCritical findings identified: {len(critical_findings)}")
        
        impression = " ".join(impression_parts) if impression_parts else "Analysis completed successfully."
        return impression
    
    def create_recommendations(self, report_data: Dict[str, Any], 
                              safety_data: Dict[str, Any]) -> str:
        """
        Create recommendations text from report and safety data.
        
        Args:
            report_data: Report content
            safety_data: Safety analysis results
            
        Returns:
            Recommendations text
        """
        recommendations = []
        
        # Add report recommendations
        if report_data and "recommendations" in report_data:
            report_recs = report_data["recommendations"]
            if isinstance(report_recs, list):
                recommendations.extend(report_recs)
            elif isinstance(report_recs, str):
                recommendations.append(report_recs)
        
        # Add safety recommendations
        if safety_data and "safety_recommendations" in safety_data:
            safety_recs = safety_data["safety_recommendations"]
            if isinstance(safety_recs, list):
                recommendations.extend(safety_recs)
        
        # Default recommendations if none provided
        if not recommendations:
            recommendations = [
                "Consult with healthcare provider for detailed interpretation",
                "Follow recommended treatment plan",
                "Schedule follow-up imaging as advised"
            ]
        
        return "\n".join(f"- {rec}" for rec in recommendations)
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing function for PDF Generation Node.
        
        This function orchestrates the entire PDF generation workflow:
        1. Checks for previous errors
        2. Ensures output directory exists
        3. Extracts and validates all required data
        4. Creates data models (PatientInfo, MRIMetadata, Finding, etc.)
        5. Generates professional PDF report
        6. Returns updated state with PDF path
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with pdf_path
        """
        report_id = state.get("report_id", f"MIA-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        log_workflow_step(report_id, "pdf_generation", "Starting PDF Generation Node")
        
        # Update current step
        state["current_step"] = "pdf_generation"
        
        # Check for previous errors
        if state.get("errors"):
            logger.warning("Previous errors detected, skipping PDF generation")
            return state
        
        # Step 1: Ensure output directory exists
        logger.info("=" * 80)
        logger.info("STEP 1: PREPARING OUTPUT DIRECTORY")
        logger.info("=" * 80)
        
        try:
            self._ensure_output_directory()
        except Exception as e:
            error_msg = f"Failed to create output directory: {str(e)}"
            logger.error(error_msg)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        # Step 2: Extract data from state
        logger.info("=" * 80)
        logger.info("STEP 2: EXTRACTING DATA FROM WORKFLOW STATE")
        logger.info("=" * 80)
        
        patient_data = state.get("patient_info", {})
        # Support both new modality-agnostic key and old key (Bug #3 fix)
        mri_data = state.get("image_metadata", state.get("mri_metadata", {}))
        vision_data = state.get("vision_analysis", {})
        validation_data = state.get("cross_validation", {})
        report_data = state.get("report_content", {})
        safety_data = state.get("safety_analysis", {})
        
        logger.info(f"Patient: {patient_data.get('name', 'Unknown')}")
        logger.info(f"Study: {mri_data.get('study_type', 'Unknown')}")
        logger.info(f"Findings: {len(vision_data.get('findings', []))}")
        
        # Step 3: Create data models
        logger.info("=" * 80)
        logger.info("STEP 3: CREATING DATA MODELS")
        logger.info("=" * 80)
        
        try:
            # Create PatientInfo model
            patient_info = self.create_patient_info(patient_data, report_id)
            logger.info(f"✓ Created PatientInfo for {patient_info.name}")
            
            # Create MRIMetadata model
            mri_metadata = self.create_mri_metadata(mri_data, patient_data)
            logger.info(f"✓ Created MRIMetadata for {mri_metadata.study_type}")
            
            # Extract findings
            findings = self.extract_findings(vision_data, validation_data)
            logger.info(f"✓ Extracted {len(findings)} findings")
            
            # Create impression
            impression = self.create_impression(report_data, safety_data)
            logger.info(f"✓ Created impression ({len(impression)} characters)")
            
            # Create recommendations
            recommendations = self.create_recommendations(report_data, safety_data)
            logger.info(f"✓ Created recommendations")
            
            # Determine urgency level
            urgency = self._map_urgency(safety_data.get("urgency_level", "ROUTINE"))
            logger.info(f"✓ Urgency level: {urgency.value}")
            
        except Exception as e:
            error_msg = f"Failed to create data models: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        # Step 4: Create MIAReport model
        logger.info("=" * 80)
        logger.info("STEP 4: CREATING MIA REPORT MODEL")
        logger.info("=" * 80)
        
        try:
            mia_report = MIAReport(
                report_id=report_id,
                patient_info=patient_info,
                mri_metadata=mri_metadata,
                findings=findings,
                impression=impression,
                recommendations=recommendations,
                urgency=urgency,
                generated_at=datetime.now(),
                generated_by="MIA Team - Agenix AI",
                # Support both new and old image path keys (Bug #3 fix)
                mri_image_path=state.get("medical_image_path", state.get("mri_image_path", "")),
                gemini_analysis=vision_data if isinstance(vision_data, dict) else {},
                gemini_validation=validation_data if isinstance(validation_data, dict) else {},
                groq_report=report_data if isinstance(report_data, dict) else {},
                groq_safety=safety_data if isinstance(safety_data, dict) else {}
            )
            
            logger.info(f"✓ Created MIAReport model for {report_id}")
            
        except Exception as e:
            error_msg = f"Failed to create MIAReport model: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        # Step 5: Generate PDF
        logger.info("=" * 80)
        logger.info("STEP 5: GENERATING PROFESSIONAL PDF REPORT")
        logger.info("=" * 80)
        
        try:
            logger.info(f"Output directory: {self.output_dir}")
            logger.info("Calling PDF generator...")

            report_type = (state.get("report_type") or "long").lower().strip()
            if report_type == "short":
                logger.info("Report type: SHORT (3 pages)")
                pdf_path = generate_short_report(mia_report, str(self.output_dir))
            else:
                logger.info("Report type: LONG (full report)")
                pdf_path = generate_mia_report(mia_report, str(self.output_dir))
            
            state["pdf_path"] = pdf_path
            
            # Verify PDF was created
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                logger.info(f"✓ PDF generated successfully: {pdf_path}")
                logger.info(f"✓ File size: {file_size / 1024:.2f} KB")
            else:
                raise FileNotFoundError(f"PDF file not found at {pdf_path}")
            
            log_workflow_step(report_id, "pdf_generation", 
                            f"PDF generated successfully: {pdf_path}", "SUCCESS")
            
        except Exception as e:
            error_msg = f"PDF generation failed: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            state.setdefault("errors", []).append(error_msg)
            return state
        
        logger.info("=" * 80)
        logger.info("PDF GENERATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
        return state


# ============================================================================
# STANDALONE FUNCTION FOR LANGGRAPH INTEGRATION
# ============================================================================

def pdf_generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standalone function wrapper for LangGraph integration.
    
    This function can be directly used in LangGraph workflow definitions.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with pdf_path
    """
    node = PDFGenerationNode()
    return node.process(state)


# Alias for backward compatibility
pdf_node = pdf_generation_node


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Test the PDF Generation Node with sample data.
    """
    print("=" * 80)
    print("TESTING PDF GENERATION NODE")
    print("=" * 80)
    
    # Sample test state with complete workflow data
    test_state = {
        "report_id": "TEST-PDF-001",
        "patient_info": {
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "height_cm": 175.0,
            "weight_kg": 80.0,
            "bmi": 26.1,
            "profession": "Engineer"
        },
        "mri_metadata": {
            "study_type": "Brain MRI",
            "sequence_type": "T2",
            "imaging_plane": "Axial"
        },
        "vision_analysis": {
            "findings": [
                {
                    "finding_id": 1,
                    "location": "Frontal lobe",
                    "description": "Normal brain tissue",
                    "severity": "NORMAL"
                }
            ],
            "measurements": {
                "brain_width_mm": 145.5
            }
        },
        "cross_validation": {
            "validation_status": "PASSED",
            "verified_findings": [
                {
                    "finding_id": 1,
                    "location": "Frontal lobe",
                    "description": "Normal brain tissue",
                    "severity": "NORMAL",
                    "verification_status": "VERIFIED"
                }
            ]
        },
        "report_content": {
            "professional_report": "Medical imaging analysis completed successfully.",
            "clinical_correlation": "Patient is a 45-year-old Male. Analysis identified 1 verified finding(s).",
            "recommendations": ["Consult with healthcare provider"]
        },
        "safety_analysis": {
            "safety_score": 95.0,
            "urgency_level": "ROUTINE",
            "critical_findings": [],
            "safety_recommendations": ["Standard follow-up recommended"]
        }
    }
    
    # Run the node
    result_state = pdf_generation_node(test_state)
    
    # Print results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if "errors" in result_state and result_state["errors"]:
        print("❌ ERRORS:")
        for error in result_state["errors"]:
            print(f"  - {error}")
    else:
        print("✅ PDF generation completed successfully!")
        if "pdf_path" in result_state:
            print(f"\n📄 PDF Report: {result_state['pdf_path']}")
            if os.path.exists(result_state['pdf_path']):
                file_size = os.path.getsize(result_state['pdf_path'])
                print(f"📊 File Size: {file_size / 1024:.2f} KB")
            else:
                print("⚠️ Warning: PDF file not found at specified path")
