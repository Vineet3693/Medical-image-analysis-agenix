"""
Enhanced PDF Generator for MIA Medical Reports
Based on FSAR reference implementation with comprehensive 10+ page reports

Features:
- Annotated MRI image generation
- Multi-page professional reports (10+ pages)
- Comprehensive findings tables
- Clinical correlation analysis
- Safety analysis with color coding
- Professional medical formatting
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm, mm
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
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging
from PIL import Image as PILImage, ImageDraw, ImageFont
import math

from config import PDF_CONFIG, SYSTEM_INFO
from models.patient_data_schema import MIAReport, Severity, UrgencyLevel

logger = logging.getLogger(__name__)

# Enhanced color scheme (FSAR-inspired)
COLORS = {
    'critical': HexColor('#DC2626'),
    'severe': HexColor('#DC2626'),
    'unsafe': HexColor('#DC2626'),
    'high': HexColor('#F59E0B'),
    'caution': HexColor('#F59E0B'),
    'moderate': HexColor('#FCD34D'),
    'mild': HexColor('#10B981'),
    'low': HexColor('#10B981'),
    'safe': HexColor('#10B981'),
    'primary': HexColor('#0066FF'),
    'text': HexColor('#1F2937'),
    'light_gray': HexColor('#F3F4F6'),
    'border': HexColor('#E5E7EB'),
}


class MRIImageAnnotator:
    """
    Generate annotated MRI images with findings highlighted
    Similar to FSAR's food image annotation
    """
    
    # Color scheme for severity levels
    SEVERITY_COLORS = {
        'CRITICAL': (220, 38, 38),      # Red
        'SEVERE': (220, 38, 38),        # Red
        'MODERATE': (245, 158, 11),     # Orange
        'MILD': (16, 185, 129),         # Green
        'MINIMAL': (16, 185, 129),      # Green
        'TEXT': (255, 255, 255),        # White
        'TEXT_BG': (0, 0, 0, 180),      # Semi-transparent black
        'BORDER': (255, 255, 255),      # White border
    }
    
    def __init__(self, report: MIAReport):
        """Initialize annotator with MIA report data"""
        self.report = report
        self.patient_info = report.patient_info
        self.findings = report.findings
        self.mri_image_path = Path(report.mri_image_path) if hasattr(report, 'mri_image_path') else None
        
        # Create output directory
        self.output_dir = Path('outputs/annotated_images')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🎨 MRI Image Annotator initialized")
        logger.info(f"📍 Image path: {self.mri_image_path}")
        logger.info(f"🔍 Findings: {len(self.findings)}")
    
    def generate_annotated_image(self) -> str:
        """
        Generate annotated MRI image with color-coded findings
        
        Returns:
            Path to annotated image file
        """
        logger.info("🎨 Starting MRI image annotation...")
        
        # Check if image exists
        if not self.mri_image_path or not self.mri_image_path.exists():
            logger.warning(f"⚠️ MRI image not found: {self.mri_image_path}")
            return ""
        
        # Load original image
        try:
            img = PILImage.open(self.mri_image_path)
            img = img.convert('RGB')
        except Exception as e:
            logger.error(f"❌ Failed to load image: {e}")
            return ""
        
        # Create annotated copy
        annotated_img = img.copy()
        draw = ImageDraw.Draw(annotated_img, 'RGBA')
        
        # Load fonts
        try:
            font_large = ImageFont.truetype("arial.ttf", 28)
            font_medium = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Image dimensions
        img_width, img_height = img.size
        
        # Add title banner
        self._add_title_banner(draw, img_width, font_large, font_medium)
        
        # Calculate annotation positions
        positions = self._calculate_positions(len(self.findings), img_width, img_height)
        
        # Annotate each finding
        for idx, finding in enumerate(self.findings):
            if idx < len(positions):
                x, y = positions[idx]
                self._draw_finding_annotation(
                    draw, x, y, finding, 
                    font_medium, font_small
                )
        
        # Add legend
        self._add_legend(draw, img_width, img_height, font_medium, font_small)
        
        # Add summary panel
        self._add_summary_panel(draw, img_width, img_height, font_medium, font_small)
        
        # Save annotated image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_name = self.patient_info.name.replace(' ', '_').lower()
        output_filename = f"annotated_mri_{patient_name}_{timestamp}.png"
        output_path = self.output_dir / output_filename
        
        annotated_img.save(output_path, 'PNG', quality=95)
        logger.info(f"✅ Annotated image saved: {output_path}")
        
        return str(output_path.resolve())
    
    def _add_title_banner(self, draw: ImageDraw, img_width: int, font_large, font_medium):
        """Add title banner to image"""
        banner_height = 80
        draw.rectangle([(0, 0), (img_width, banner_height)], fill=(0, 0, 0, 200))
        
        title = "MRI ANALYSIS REPORT"
        patient_name = self.patient_info.name
        
        # Center title
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((img_width - title_width) // 2, 15),
            title,
            fill=self.SEVERITY_COLORS['TEXT'],
            font=font_large
        )
        
        # Subtitle
        subtitle = f"Patient: {patient_name} | ID: {self.report.report_id}"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(
            ((img_width - subtitle_width) // 2, 50),
            subtitle,
            fill=self.SEVERITY_COLORS['TEXT'],
            font=font_medium
        )
    
    def _calculate_positions(self, num_findings: int, img_width: int, img_height: int) -> List[Tuple[int, int]]:
        """Calculate positions for finding annotations"""
        positions = []
        margin_x, margin_y = 80, 100
        title_space, legend_space = 90, 140
        
        usable_width = img_width - 2 * margin_x
        usable_height = img_height - title_space - legend_space - margin_y
        
        # Determine grid layout
        if num_findings <= 3:
            cols = num_findings
        elif num_findings <= 6:
            cols = 3
        elif num_findings <= 12:
            cols = 4
        else:
            cols = 5
        
        rows = (num_findings + cols - 1) // cols
        spacing_x = usable_width // cols if cols > 0 else usable_width
        spacing_y = usable_height // rows if rows > 0 else usable_height
        
        for i in range(num_findings):
            row, col = i // cols, i % cols
            x = margin_x + col * spacing_x + spacing_x // 2
            y = title_space + margin_y // 2 + row * spacing_y + spacing_y // 2
            positions.append((x, y))
        
        return positions
    
    def _draw_finding_annotation(self, draw: ImageDraw, x: int, y: int, 
                                 finding, font_medium, font_small):
        """Draw annotation for a single finding"""
        # Get severity color
        severity = finding.severity.value if hasattr(finding.severity, 'value') else str(finding.severity)
        color = self.SEVERITY_COLORS.get(severity.upper(), self.SEVERITY_COLORS['MODERATE'])
        
        # Finding name
        name = finding.location[:20] if len(finding.location) > 20 else finding.location
        
        # Draw text background
        name_bbox = draw.textbbox((0, 0), name, font=font_medium)
        name_w, name_h = name_bbox[2] - name_bbox[0], name_bbox[3] - name_bbox[1]
        
        text_x, text_y = x + 60 - name_w // 2, y
        padding = 4
        
        draw.rectangle(
            [(text_x - padding, text_y - padding),
             (text_x + name_w + padding, text_y + name_h + padding)],
            fill=(0, 0, 0, 200)
        )
        
        # Draw text
        draw.text((text_x, text_y), name, fill=color, font=font_medium)
        
        # Draw arrow
        ax1, ay1 = text_x - padding, text_y + name_h // 2
        draw.line([(ax1, ay1), (x, y)], fill=color, width=3)
        
        # Arrowhead
        dx, dy = x - ax1, y - ay1
        angle = math.atan2(dy, dx)
        asize = 8
        tip = (x, y)
        p1 = (x - asize * math.cos(angle - math.pi/6), y - asize * math.sin(angle - math.pi/6))
        p2 = (x - asize * math.cos(angle + math.pi/6), y - asize * math.sin(angle + math.pi/6))
        draw.polygon([tip, p1, p2], fill=color)
    
    def _add_legend(self, draw: ImageDraw, img_width: int, img_height: int, 
                   font_medium, font_small):
        """Add severity legend"""
        ly, lx = img_height - 120, 20
        draw.rectangle([(lx-10, ly-10), (lx+280, ly+90)], fill=(0, 0, 0, 180))
        draw.text((lx, ly), "Severity Legend:", fill=(255, 255, 255), font=font_medium)
        
        items = [
            ('CRITICAL', 'Immediate attention', self.SEVERITY_COLORS['CRITICAL']),
            ('MODERATE', 'Monitor closely', self.SEVERITY_COLORS['MODERATE']),
            ('MILD', 'Routine follow-up', self.SEVERITY_COLORS['MILD'])
        ]
        
        for i, (level, desc, color) in enumerate(items):
            yo = ly + 25 + i * 20
            draw.ellipse([(lx, yo), (lx+15, yo+15)], fill=color, outline=(255, 255, 255), width=2)
            draw.text((lx+25, yo), desc, fill=(255, 255, 255), font=font_small)
    
    def _add_summary_panel(self, draw: ImageDraw, img_width: int, img_height: int,
                          font_medium, font_small):
        """Add summary statistics panel"""
        px, py = img_width - 280, img_height - 150
        
        # Count by severity
        critical = sum(1 for f in self.findings if 'CRITICAL' in str(f.severity).upper())
        moderate = sum(1 for f in self.findings if 'MODERATE' in str(f.severity).upper())
        mild = sum(1 for f in self.findings if 'MILD' in str(f.severity).upper())
        
        draw.rectangle([(px-10, py-10), (img_width-10, py+120)], fill=(0, 0, 0, 180))
        draw.text((px, py), "Summary:", fill=(255, 255, 255), font=font_medium)
        
        stats = [
            f"Total Findings: {len(self.findings)}",
            f"Critical: {critical} | Moderate: {moderate} | Mild: {mild}",
            f"Date: {datetime.now().strftime('%Y-%m-%d')}"
        ]
        
        for i, txt in enumerate(stats):
            draw.text((px, py + 25 + i * 20), txt, fill=(255, 255, 255), font=font_small)


def get_enhanced_styles():
    """Get enhanced paragraph styles for medical reports"""
    styles = getSampleStyleSheet()
    
    # Section Title
    if 'SectionTitle' not in styles:
        styles.add(ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=COLORS['primary'],
            spaceAfter=15,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        ))
    
    # SubSection
    if 'SubSection' not in styles:
        styles.add(ParagraphStyle(
            'SubSection',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=COLORS['text'],
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))
    
    # BodyText
    if 'BodyText' not in styles:
        styles.add(ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLORS['text'],
            spaceAfter=8,
            fontName='Helvetica',
            alignment=TA_JUSTIFY
        ))
    
    # TableHeader
    if 'TableHeader' not in styles:
        styles.add(ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
    
    # TableCell
    if 'TableCell' not in styles:
        styles.add(ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=7,
            textColor=COLORS['text'],
            fontName='Helvetica',
            alignment=TA_LEFT
        ))
    
    return styles


# This file will continue in the next message due to length...
