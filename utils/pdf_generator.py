"""
PDF Generator for MIA Medical Reports
Generates professional A4 PDF reports with patient details, MRI images, and analysis
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from PIL import Image as PILImage
import io

from config import PDF_CONFIG, SYSTEM_INFO
from models.patient_data_schema import MIAReport

logger = logging.getLogger(__name__)


# Color scheme for severity levels (from FIP pattern)
COLORS = {
    'critical': colors.HexColor('#DC2626'),
    'severe': colors.HexColor('#DC2626'),
    'high': colors.HexColor('#F59E0B'),
    'moderate': colors.HexColor('#FCD34D'),
    'mild': colors.HexColor('#10B981'),
    'low': colors.HexColor('#10B981'),
    'primary': colors.HexColor('#0066FF'),
    'text': colors.HexColor('#1F2937'),
    'light_gray': colors.HexColor('#F3F4F6'),
    'border': colors.HexColor('#E5E7EB'),
}


class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas with watermark and page numbers
    Based on FIP report generator pattern
    """
    
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
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        page_num = self._pageNumber
        
        # Watermark
        if Path(self.logo_path).exists():
            try:
                self.saveState()
                self.setFillAlpha(PDF_CONFIG["branding"]["watermark_opacity"])
                logo_size = 4 * inch
                x = (A4[0] - logo_size) / 2
                y = (A4[1] - logo_size) / 2
                self.drawImage(
                    self.logo_path, x, y, 
                    width=logo_size, 
                    height=logo_size,
                    mask='auto', 
                    preserveAspectRatio=True
                )
                self.restoreState()
            except Exception as e:
                logger.warning(f"Could not add watermark: {e}")
        
        # Header (skip on first page)
        if page_num > 1:
            self.saveState()
            self.setFont('Helvetica-Bold', 10)
            self.setFillColor(COLORS['primary'])
            self.drawString(
                0.75 * inch, 
                A4[1] - 0.5 * inch, 
                PDF_CONFIG["branding"]["header_text"]
            )
            self.setStrokeColor(COLORS['border'])
            self.setLineWidth(0.5)
            self.line(
                0.75 * inch, 
                A4[1] - 0.6 * inch, 
                A4[0] - 0.75 * inch, 
                A4[1] - 0.6 * inch
            )
            self.restoreState()
        
        # Footer
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColor(COLORS['text'])
        self.drawCentredString(
            A4[0] / 2, 
            0.5 * inch, 
            f"Page {page_num} of {page_count}"
        )
        self.setStrokeColor(COLORS['border'])
        self.setLineWidth(0.5)
        self.line(
            0.75 * inch, 
            0.7 * inch, 
            A4[0] - 0.75 * inch, 
            0.7 * inch
        )
        self.restoreState()



class MIAPDFGenerator:
    """Generate professional PDF reports for MIA analysis"""
    
    def __init__(self, output_path: Path):
        """
        Initialize PDF generator with NumberedCanvas
        
        Args:
            output_path: Path where PDF will be saved
        """
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            topMargin=PDF_CONFIG["margin_top"],
            bottomMargin=PDF_CONFIG["margin_bottom"],
            leftMargin=PDF_CONFIG["margin_left"],
            rightMargin=PDF_CONFIG["margin_right"]
        )
        self.styles = self._create_styles()
        self.story = []
        self.page_number = 0
        
        logger.info(f"Initialized PDF generator with NumberedCanvas: {output_path}")
        
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=PDF_CONFIG["fonts"]["title"]["size"],
            textColor=colors.HexColor('#003366'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=PDF_CONFIG["fonts"]["heading"]["size"],
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subheading style
        styles.add(ParagraphStyle(
            name='CustomSubheading',
            parent=styles['Heading3'],
            fontSize=PDF_CONFIG["fonts"]["subheading"]["size"],
            textColor=colors.HexColor('#666666'),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body style
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=PDF_CONFIG["fonts"]["body"]["size"],
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Small text style
        styles.add(ParagraphStyle(
            name='CustomSmall',
            parent=styles['Normal'],
            fontSize=PDF_CONFIG["fonts"]["small"]["size"],
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica'
        ))
        
        return styles
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to each page"""
        canvas_obj.saveState()
        
        # Header
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.HexColor('#003366'))
        canvas_obj.drawString(
            PDF_CONFIG["margin_left"],
            A4[1] - 40,
            PDF_CONFIG["branding"]["header_text"]
        )
        
        # Header line
        canvas_obj.setStrokeColor(colors.HexColor('#003366'))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(
            PDF_CONFIG["margin_left"],
            A4[1] - 50,
            A4[0] - PDF_CONFIG["margin_right"],
            A4[1] - 50
        )
        
        # Footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        
        # Footer text
        footer_text = PDF_CONFIG["branding"]["footer_text"]
        canvas_obj.drawString(
            PDF_CONFIG["margin_left"],
            30,
            footer_text
        )
        
        # Page number
        page_num = f"Page {doc.page}"
        canvas_obj.drawRightString(
            A4[0] - PDF_CONFIG["margin_right"],
            30,
            page_num
        )
        
        # Watermark (if logo exists)
        logo_path = PDF_CONFIG["logo"]["path"]
        if logo_path.exists():
            try:
                canvas_obj.saveState()
                canvas_obj.setFillAlpha(PDF_CONFIG["branding"]["watermark_opacity"])
                canvas_obj.drawImage(
                    str(logo_path),
                    A4[0]/2 - PDF_CONFIG["logo"]["watermark_width"]/2,
                    A4[1]/2 - PDF_CONFIG["logo"]["watermark_height"]/2,
                    width=PDF_CONFIG["logo"]["watermark_width"],
                    height=PDF_CONFIG["logo"]["watermark_height"],
                    mask='auto',
                    preserveAspectRatio=True
                )
                canvas_obj.restoreState()
            except Exception as e:
                logger.warning(f"Could not add watermark: {e}")
        
        canvas_obj.restoreState()
    
    def _create_separator_line(self, width: int = 500) -> Table:
        """Create a horizontal separator line"""
        data = [['─' * 80]]
        table = Table(data, colWidths=[width])
        table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#003366')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        return table
    
    def generate_page_1_patient_info(self, report: MIAReport):
        """Generate Page 1: Patient Information"""
        logger.info("Generating Page 1: Patient Information")
        
        # Title
        title = Paragraph(
            PDF_CONFIG["branding"]["header_text"],
            self.styles['CustomTitle']
        )
        subtitle = Paragraph(
            PDF_CONFIG["branding"]["subtitle_text"],
            self.styles['CustomTitle']
        )
        
        self.story.append(Spacer(1, 30))
        self.story.append(title)
        self.story.append(subtitle)
        self.story.append(Spacer(1, 20))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 20))
        
        # Patient Information Section
        self.story.append(Paragraph("PATIENT INFORMATION", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        
        patient_data = [
            ["Patient Name:", report.patient_info.name],
            ["Patient ID:", report.patient_info.patient_id or "N/A"],
            ["Age:", f"{report.patient_info.age} years"],
            ["Gender:", report.patient_info.gender],
            ["Height:", f"{report.patient_info.height_cm} cm"],
            ["BMI:", f"{report.patient_info.bmi} kg/m²"],
            ["Profession:", report.patient_info.profession],
        ]
        
        patient_table = Table(patient_data, colWidths=[150, 300])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(patient_table)
        self.story.append(Spacer(1, 20))
        
        # Study Information Section
        self.story.append(Paragraph("STUDY INFORMATION", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        
        study_data = [
            ["Study Date:", report.mri_metadata.study_date.strftime("%Y-%m-%d")],
            ["Study Type:", report.mri_metadata.study_type],
            ["Sequence:", report.mri_metadata.sequence_type],
            ["Imaging Plane:", report.mri_metadata.imaging_plane],
            ["Report Date:", report.generated_at.strftime("%Y-%m-%d")],
            ["Report ID:", report.report_id],
        ]
        
        study_table = Table(study_data, colWidths=[150, 300])
        study_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(study_table)
        self.story.append(Spacer(1, 30))
        
        # Confidential footer
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        confidential = Paragraph(
            "CONFIDENTIAL MEDICAL DOCUMENT",
            self.styles['CustomTitle']
        )
        self.story.append(confidential)
        
        # Page break
        self.story.append(PageBreak())
    
    def generate_page_2_imaging(self, report: MIAReport):
        """Generate Page 2: MRI Image Display"""
        logger.info("Generating Page 2: MRI Image Display")
        
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph("IMAGING STUDIES", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 20))
        
        # Add MRI image
        if Path(report.mri_image_path).exists():
            try:
                img = Image(
                    report.mri_image_path,
                    width=PDF_CONFIG["image"]["max_width"],
                    height=PDF_CONFIG["image"]["max_height"]
                )
                img.hAlign = 'CENTER'
                self.story.append(img)
                self.story.append(Spacer(1, 15))
            except Exception as e:
                logger.error(f"Error adding MRI image: {e}")
                self.story.append(Paragraph(
                    f"[Image could not be loaded: {report.mri_image_path}]",
                    self.styles['CustomBody']
                ))
        
        # Image details
        self.story.append(Paragraph("Image Details:", self.styles['CustomSubheading']))
        
        image_details = [
            ["Sequence Type:", report.mri_metadata.sequence_type],
            ["Plane:", report.mri_metadata.imaging_plane],
            ["Image Quality:", report.mri_metadata.image_quality],
        ]
        
        details_table = Table(image_details, colWidths=[150, 300])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(details_table)
        self.story.append(Spacer(1, 15))
        
        # Technical parameters
        self.story.append(Paragraph("Technical Parameters:", self.styles['CustomSubheading']))
        
        tech_details = [
            ["Field Strength:", report.mri_metadata.field_strength or "Not specified"],
            ["Contrast:", "Yes" if report.mri_metadata.contrast_used else "No"],
            ["Artifacts:", "Yes" if report.mri_metadata.artifacts_present else "None"],
        ]
        
        tech_table = Table(tech_details, colWidths=[150, 300])
        tech_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        self.story.append(tech_table)
        
        # Page break
        self.story.append(PageBreak())
    
    def generate_page_3_analysis(self, report: MIAReport):
        """Generate Page 3+: Detailed Analysis"""
        logger.info("Generating Page 3+: Detailed Analysis")
        
        report_data = report.report_content.page_3_analysis
        
        # FINDINGS Section
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph("FINDINGS", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        
        # Technique
        self.story.append(Paragraph("TECHNIQUE", self.styles['CustomSubheading']))
        self.story.append(Paragraph(
            report_data.get("technique", "MRI imaging performed as described above."),
            self.styles['CustomBody']
        ))
        self.story.append(Spacer(1, 10))
        
        # Image Quality
        self.story.append(Paragraph("IMAGE QUALITY", self.styles['CustomSubheading']))
        self.story.append(Paragraph(
            report_data.get("image_quality", "Image quality is adequate for diagnostic interpretation."),
            self.styles['CustomBody']
        ))
        self.story.append(Spacer(1, 10))
        
        # Anatomical Structures
        self.story.append(Paragraph("ANATOMICAL STRUCTURES", self.styles['CustomSubheading']))
        self.story.append(Paragraph(
            report_data.get("anatomical_structures", "Normal anatomical structures visualized."),
            self.styles['CustomBody']
        ))
        self.story.append(Spacer(1, 10))
        
        # Abnormal Findings
        self.story.append(Paragraph("ABNORMAL FINDINGS", self.styles['CustomSubheading']))
        findings = report_data.get("findings", [])
        
        if findings:
            for i, finding in enumerate(findings, 1):
                finding_text = f"<b>Finding {i}: {finding.get('location', 'Unknown location')}</b><br/>"
                finding_text += f"• Description: {finding.get('description', 'No description')}<br/>"
                
                if finding.get('measurements'):
                    finding_text += f"• Measurements: {finding['measurements']}<br/>"
                
                finding_text += f"• Signal Characteristics: {finding.get('signal_characteristics', 'Not specified')}<br/>"
                finding_text += f"• Clinical Significance: {finding.get('clinical_significance', 'Not specified')}"
                
                self.story.append(Paragraph(finding_text, self.styles['CustomBody']))
                self.story.append(Spacer(1, 8))
        else:
            self.story.append(Paragraph("No significant abnormal findings identified.", self.styles['CustomBody']))
        
        self.story.append(Spacer(1, 15))
        
        # IMPRESSION Section
        self.story.append(self._create_separator_line())
        self.story.append(Paragraph("IMPRESSION", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        
        impressions = report_data.get("impression", [])
        for i, impression in enumerate(impressions, 1):
            self.story.append(Paragraph(f"{i}. {impression}", self.styles['CustomBody']))
            self.story.append(Spacer(1, 6))
        
        self.story.append(Spacer(1, 10))
        
        # Differential Diagnosis
        self.story.append(Paragraph("DIFFERENTIAL DIAGNOSIS", self.styles['CustomSubheading']))
        self.story.append(Spacer(1, 6))
        
        diff_diagnoses = report_data.get("differential_diagnosis", [])
        for i, dd in enumerate(diff_diagnoses, 1):
            dd_text = f"<b>{i}. {dd.get('diagnosis', 'Unknown')} - {dd.get('probability', 'Unknown')} PROBABILITY</b><br/>"
            dd_text += f"Supporting features: {', '.join(dd.get('supporting_features', []))}"
            self.story.append(Paragraph(dd_text, self.styles['CustomBody']))
            self.story.append(Spacer(1, 8))
        
        # Page break before recommendations
        self.story.append(PageBreak())
        
        # CLINICAL CORRELATION Section
        self.story.append(Spacer(1, 20))
        self.story.append(Paragraph("CLINICAL CORRELATION", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        
        clinical_corr = report_data.get("clinical_correlation", {})
        
        if clinical_corr.get("age_considerations"):
            self.story.append(Paragraph("AGE-RELATED CONSIDERATIONS", self.styles['CustomSubheading']))
            self.story.append(Paragraph(clinical_corr["age_considerations"], self.styles['CustomBody']))
            self.story.append(Spacer(1, 8))
        
        if clinical_corr.get("profession_factors"):
            self.story.append(Paragraph("PROFESSION-RELATED FACTORS", self.styles['CustomSubheading']))
            self.story.append(Paragraph(clinical_corr["profession_factors"], self.styles['CustomBody']))
            self.story.append(Spacer(1, 8))
        
        if clinical_corr.get("bmi_considerations"):
            self.story.append(Paragraph("BMI AND METABOLIC CONSIDERATIONS", self.styles['CustomSubheading']))
            self.story.append(Paragraph(clinical_corr["bmi_considerations"], self.styles['CustomBody']))
            self.story.append(Spacer(1, 8))
        
        self.story.append(Spacer(1, 15))
        
        # RECOMMENDATIONS Section
        self.story.append(self._create_separator_line())
        self.story.append(Paragraph("RECOMMENDATIONS", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        
        recommendations = report_data.get("recommendations", {})
        
        urgency = recommendations.get("urgency_level", "ROUTINE")
        urgency_color = {
            "IMMEDIATE": colors.red,
            "URGENT": colors.orange,
            "SEMI-URGENT": colors.yellow,
            "ROUTINE": colors.green
        }.get(urgency, colors.black)
        
        urgency_para = Paragraph(
            f"<b>URGENCY LEVEL: <font color='{urgency_color.hexval()}'>{urgency}</font></b>",
            self.styles['CustomBody']
        )
        self.story.append(urgency_para)
        self.story.append(Spacer(1, 10))
        
        if recommendations.get("immediate_actions"):
            self.story.append(Paragraph("IMMEDIATE ACTIONS", self.styles['CustomSubheading']))
            for action in recommendations["immediate_actions"]:
                self.story.append(Paragraph(f"• {action}", self.styles['CustomBody']))
            self.story.append(Spacer(1, 8))
        
        if recommendations.get("follow_up_imaging"):
            self.story.append(Paragraph("FOLLOW-UP IMAGING", self.styles['CustomSubheading']))
            self.story.append(Paragraph(recommendations["follow_up_imaging"], self.styles['CustomBody']))
            self.story.append(Spacer(1, 8))
        
        if recommendations.get("specialist_referrals"):
            self.story.append(Paragraph("SPECIALIST REFERRALS", self.styles['CustomSubheading']))
            for referral in recommendations["specialist_referrals"]:
                self.story.append(Paragraph(f"• {referral}", self.styles['CustomBody']))
            self.story.append(Spacer(1, 8))
        
        if recommendations.get("patient_counseling"):
            self.story.append(Paragraph("PATIENT COUNSELING POINTS", self.styles['CustomSubheading']))
            for point in recommendations["patient_counseling"]:
                self.story.append(Paragraph(f"• {point}", self.styles['CustomBody']))
        
        self.story.append(Spacer(1, 15))
        
        # Quality Assurance
        self.story.append(self._create_separator_line())
        self.story.append(Paragraph("QUALITY ASSURANCE", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        
        qa = report_data.get("quality_assurance", {})
        qa_text = f"Analysis Confidence: {qa.get('confidence_score', 0)*100:.1f}%<br/>"
        qa_text += f"Cross-Validation Status: {qa.get('validation_status', 'Unknown')}<br/>"
        if qa.get('notes'):
            qa_text += f"Quality Assurance Notes: {qa['notes']}"
        
        self.story.append(Paragraph(qa_text, self.styles['CustomBody']))
        self.story.append(Spacer(1, 15))
        
        # Disclaimer
        self.story.append(self._create_separator_line())
        self.story.append(Paragraph("DISCLAIMER", self.styles['CustomHeading']))
        self.story.append(self._create_separator_line())
        self.story.append(Spacer(1, 10))
        
        disclaimer = report_data.get("disclaimer", report.safety_analysis.final_disclaimer.get("disclaimer_text", ""))
        self.story.append(Paragraph(disclaimer, self.styles['CustomSmall']))
        
        self.story.append(Spacer(1, 20))
        
        # Footer info
        footer_info = f"Generated by: {SYSTEM_INFO['organization']}<br/>"
        footer_info += f"Report Version: {SYSTEM_INFO['version']}<br/>"
        footer_info += f"Analysis Date: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        footer_info += f"System Version: {SYSTEM_INFO['version']}"
        
        self.story.append(Paragraph(footer_info, self.styles['CustomSmall']))
    
    def generate(self, report: MIAReport) -> Path:
        """
        Generate complete PDF report with NumberedCanvas
        
        Args:
            report: Complete MIA report data
            
        Returns:
            Path to generated PDF file
        """
        logger.info(f"Generating PDF report: {self.output_path}")
        
        # Generate all pages
        self.generate_page_1_patient_info(report)
        self.generate_page_2_imaging(report)
        self.generate_page_3_analysis(report)
        
        # Build PDF with NumberedCanvas
        self.doc.build(
            self.story,
            canvasmaker=NumberedCanvas
        )
        
        logger.info(f"PDF report generated successfully: {self.output_path}")
        return self.output_path


def generate_mia_report(report: MIAReport, output_dir: Path) -> Path:
    """
    Convenience function to generate MIA PDF report
    
    Args:
        report: Complete MIA report data
        output_dir: Directory to save PDF
        
    Returns:
        Path to generated PDF
    """
    # Convert to Path if string
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    filename = f"{report.patient_info.patient_id or 'patient'}_{report.report_id}.pdf"
    output_path = output_dir / filename
    
    generator = MIAPDFGenerator(output_path)
    return generator.generate(report)
