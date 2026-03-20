"""
MIA Enhanced PDF Generator - Complete Implementation
Generates comprehensive 10+ page medical reports with annotated images

Features:
- 10+ page professional medical reports
- Annotated MRI images with color-coded findings
- Comprehensive findings tables
- Clinical correlation and safety analysis
- Professional formatting with watermarks
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging
from PIL import Image as PILImage, ImageDraw, ImageFont
import math

logger = logging.getLogger(__name__)

# Color scheme
COLORS = {
    'critical': HexColor('#DC2626'),
    'severe': HexColor('#DC2626'),
    'high': HexColor('#F59E0B'),
    'moderate': HexColor('#FCD34D'),
    'mild': HexColor('#10B981'),
    'safe': HexColor('#10B981'),
    'primary': HexColor('#0066FF'),
    'text': HexColor('#1F2937'),
    'light_gray': HexColor('#F3F4F6'),
    'border': HexColor('#E5E7EB'),
}


class NumberedCanvas(canvas.Canvas):
    """Custom canvas with watermark and page numbers"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.logo_path = kwargs.get('logo_path', 'assets/agenix_logo.png')

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
                self.setFillAlpha(0.05)
                logo_size = 4 * inch
                x, y = (A4[0] - logo_size) / 2, (A4[1] - logo_size) / 2
                self.drawImage(self.logo_path, x, y, width=logo_size, height=logo_size,
                             mask='auto', preserveAspectRatio=True)
                self.restoreState()
            except:
                pass
        
        # Header (skip on first page)
        if page_num > 1:
            self.saveState()
            self.setFont('Helvetica-Bold', 10)
            self.setFillColor(COLORS['primary'])
            self.drawString(0.75 * inch, A4[1] - 0.5 * inch, "AGENIX AI TEAM - MIA REPORT")
            self.setStrokeColor(COLORS['border'])
            self.setLineWidth(0.5)
            self.line(0.75 * inch, A4[1] - 0.6 * inch, A4[0] - 0.75 * inch, A4[1] - 0.6 * inch)
            self.restoreState()
        
        # Footer
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColor(COLORS['text'])
        self.drawCentredString(A4[0] / 2, 0.5 * inch, f"Page {page_num} of {page_count}")
        self.setStrokeColor(COLORS['border'])
        self.setLineWidth(0.5)
        self.line(0.75 * inch, 0.7 * inch, A4[0] - 0.75 * inch, 0.7 * inch)
        self.restoreState()


def get_styles():
    """Get enhanced paragraph styles"""
    styles = getSampleStyleSheet()
    
    if 'SectionTitle' not in styles:
        styles.add(ParagraphStyle(
            'SectionTitle', parent=styles['Heading1'], fontSize=18,
            textColor=COLORS['primary'], spaceAfter=15, fontName='Helvetica-Bold'
        ))
    
    if 'SubSection' not in styles:
        styles.add(ParagraphStyle(
            'SubSection', parent=styles['Heading2'], fontSize=14,
            textColor=COLORS['text'], spaceAfter=10, fontName='Helvetica-Bold'
        ))
    
    if 'BodyText' not in styles:
        styles.add(ParagraphStyle(
            'BodyText', parent=styles['Normal'], fontSize=10,
            textColor=COLORS['text'], spaceAfter=8, fontName='Helvetica', alignment=TA_JUSTIFY
        ))
    
    if 'TableHeader' not in styles:
        styles.add(ParagraphStyle(
            'TableHeader', parent=styles['Normal'], fontSize=8,
            textColor=colors.white, fontName='Helvetica-Bold', alignment=TA_CENTER
        ))
    
    if 'TableCell' not in styles:
        styles.add(ParagraphStyle(
            'TableCell', parent=styles['Normal'], fontSize=7,
            textColor=COLORS['text'], fontName='Helvetica', alignment=TA_LEFT
        ))
    
    return styles


def generate_mia_report_enhanced(report, output_dir: str) -> str:
    """
    Generate enhanced 10+ page MIA report
    
    Args:
        report: MIAReport object with all analysis data
        output_dir: Directory to save PDF
        
    Returns:
        Path to generated PDF
    """
    logger.info("📄 Generating Enhanced MIA Report (10+ pages)")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    patient_id = report.patient_info.patient_id or "UNKNOWN"
    pdf_filename = f"MIA_Enhanced_{patient_id}_{timestamp}.pdf"
    pdf_path = output_path / pdf_filename
    
    # Logo path
    logo_path = "assets/agenix_logo.png"
    if not Path(logo_path).exists():
        logo_path = "e:/MIA/assets/agenix_logo.png"
    
    # Create document
    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=1*inch, bottomMargin=1*inch
    )
    
    # Build story
    story = []
    styles = get_styles()
    
    # Page 1: Cover Page
    logger.info("Adding Page 1: Cover Page")
    story.extend(create_cover_page(report, styles, logo_path))
    story.append(PageBreak())
    
    # Page 2: Findings Summary Table
    logger.info("Adding Page 2: Findings Summary Table")
    story.extend(create_findings_table(report, styles))
    story.append(PageBreak())
    
    # Page 3: Annotated MRI Image
    logger.info("Adding Page 3: Annotated MRI Image")
    story.extend(create_annotated_image_page(report, styles))
    story.append(PageBreak())
    
    # Page 4-5: Detailed Findings Analysis
    logger.info("Adding Pages 4-5: Detailed Findings Analysis")
    story.extend(create_detailed_findings(report, styles))
    story.append(PageBreak())
    
    # Page 6: Cross-Validation Results
    logger.info("Adding Page 6: Cross-Validation Results")
    story.extend(create_validation_page(report, styles))
    story.append(PageBreak())
    
    # Page 7: Clinical Correlation
    logger.info("Adding Page 7: Clinical Correlation")
    story.extend(create_clinical_correlation(report, styles))
    story.append(PageBreak())
    
    # Page 8: Safety Analysis
    logger.info("Adding Page 8: Safety Analysis")
    story.extend(create_safety_analysis(report, styles))
    story.append(PageBreak())
    
    # Page 9: Recommendations
    logger.info("Adding Page 9: Recommendations")
    story.extend(create_recommendations_page(report, styles))
    story.append(PageBreak())
    
    # Page 10: Statistical Summary & Appendix
    logger.info("Adding Page 10: Statistical Summary & Appendix")
    story.extend(create_appendix(report, styles))
    
    # Build PDF with custom canvas
    logger.info("Building PDF with NumberedCanvas...")
    doc.build(story, canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, logo_path=logo_path, **kwargs))
    
    logger.info(f"✅ Enhanced MIA Report generated: {pdf_path}")
    return str(pdf_path)


# Page generation functions will continue in next part...
