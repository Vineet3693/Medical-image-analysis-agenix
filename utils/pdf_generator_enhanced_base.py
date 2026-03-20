"""
FIP_report_generator_fsar.py
================================================================================
FSAR REPORT GENERATOR - Food Safety & Risk Assessment Report

Based on FIP_report_generator_complete.py with table-based Page 2.

Generates comprehensive PDF report with:
- Page 1: Cover Page (same as original)
- Page 2: FSAR Table (NEW - organized by risk level)
- Pages 3-4: Detailed Food Item Analysis
- Page 5: Nutritional Compliance
- Page 6: Medical Interactions & Warnings
- Page 7: Personalized Recommendations
- Page 8: Medical Purpose Insights
- Page 9: Statistical Summary
- Page 10: Appendix & Disclaimers

================================================================================
"""

from typing import Dict, Any, List, Tuple
import json
import sys
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from config.settings import settings
from src.logging.logger import logger
from src.exception.exception import LLMException
from PIL import Image as PilImage, ImageDraw, ImageFont
import math

FIPState = Dict[str, Any]

# Color scheme (same as original)
COLORS = {
    'critical': HexColor('#DC2626'), 'unsafe': HexColor('#DC2626'),
    'high': HexColor('#F59E0B'), 'caution': HexColor('#F59E0B'),
    'moderate': HexColor('#FCD34D'),
    'low': HexColor('#10B981'), 'safe': HexColor('#10B981'),
    'primary': HexColor('#0066FF'), 'text': HexColor('#1F2937'),
    'light_gray': HexColor('#F3F4F6'), 'border': HexColor('#E5E7EB'),
}


class AnnotatedReportGenerator:
    """
    Generates annotated food images with safety indicators and comprehensive health analysis.
    """
    
    # Color scheme for safety levels
    COLORS = {
        'SAFE': (46, 204, 113),      # Green
        'CAUTION': (241, 196, 15),   # Yellow
        'UNSAFE': (231, 76, 60),     # Red
        'TEXT': (255, 255, 255),     # White
        'TEXT_BG': (0, 0, 0, 180),   # Semi-transparent black
        'BORDER': (255, 255, 255),   # White border
    }
    
    def __init__(self, state: FIPState):
        """
        Initialize the annotated report generator from state.
        
        Args:
            state: The current FIP state
        """
        self.state = state
        self.patient_info = state.get('patient_info', {})
        self.blood_group = self.patient_info.get('blood_group', 'Unknown')
        self.profession = self.patient_info.get('profession', 'Unknown')
        
        # Extract key data
        self.food_items = self.state.get('identified_food_items', [])
        self.risk_analysis = self.state.get('food_item_risk_analysis', [])
        self.image_path = Path(self.state.get('uploaded_image_path', ''))
        
        # Create output directory
        self.output_dir = Path('data/outputs/annotated_reports')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📸 Food image: {self.image_path}")
        logger.info(f"🍽️  Food items: {len(self.food_items)}")
    
    def get_risk_level_for_food(self, food_name: str) -> str:
        """Get risk level for a specific food item."""
        for item in self.risk_analysis:
            if item['name'] == food_name:
                return item.get('risk_level', 'CAUTION')
        return 'CAUTION'
    
    def get_calories_for_food(self, food_name: str) -> int:
        """Get calorie count for a specific food item."""
        for item in self.food_items:
            if item['name'] == food_name:
                return item.get('calories', 0)
        return 0
    
    def generate_annotated_image(self) -> str:
        """
        Generate annotated food image with safety indicators.
        
        Returns:
            String path to the generated annotated image
        """
        logger.info("🎨 Starting image annotation inside FSAR node...")
        
        # Load the original image
        if not self.image_path.exists():
            # Try to find it in default uploads if relative path fails
            if not self.image_path.is_absolute():
                alt_path = Path("e:/fip") / self.image_path
                if alt_path.exists():
                    self.image_path = alt_path
            
            if not self.image_path.exists():
                raise FileNotFoundError(f"Image not found at {self.image_path}")
        
        img = PilImage.open(self.image_path)
        img = img.convert('RGB')
        
        # Create a copy for annotation
        annotated_img = img.copy()
        draw = ImageDraw.Draw(annotated_img, 'RGBA')
        
        # Load fonts
        try:
            # Try arial first, fall back to default
            font_medium = ImageFont.truetype("arial.ttf", 14) 
            font_small = ImageFont.truetype("arial.ttf", 12)   
            font_title = ImageFont.truetype("arialbd.ttf", 28) 
        except:
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_title = ImageFont.load_default()
        
        # Image dimensions
        img_width, img_height = img.size
        
        # Add title banner
        self._add_title_banner(draw, img_width, font_title, font_medium)
        
        # Calculate positions
        positions = self._calculate_annotation_positions(len(self.food_items), img_width, img_height)
        
        # Annotate items
        for idx, food_item in enumerate(self.food_items):
            food_name = food_item['name']
            calories = food_item.get('calories', 0)
            risk_level = self.get_risk_level_for_food(food_name)
            x, y = positions[idx]
            self._draw_food_annotation(draw, x, y, food_name, calories, risk_level, font_medium, font_small)
        
        # Add legend and summary
        self._add_legend(draw, img_width, img_height, font_medium, font_small)
        self._add_summary_panel(draw, img_width, img_height, font_medium, font_small)
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_name = self.patient_info.get('name', 'unknown').replace(' ', '_').lower()
        output_filename = f"annotated_food_report_{patient_name}_{timestamp}.png"
        output_path = self.output_dir / output_filename
        
        annotated_img.save(output_path, 'PNG', quality=95)
        logger.info(f"✅ Annotated image generated and saved: {output_path}")
        
        return str(output_path.resolve())

    def _add_title_banner(self, draw: ImageDraw, img_width: int, font_title, font_medium):
        banner_height = 80
        draw.rectangle([(0, 0), (img_width, banner_height)], fill=(0, 0, 0, 200))
        title = "FOOD SAFETY ANALYSIS REPORT"
        patient_name = self.patient_info.get('name', 'Unknown')
        
        title_bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((img_width - title_width) // 2, 15), title, fill=self.COLORS['TEXT'], font=font_title)
        
        subtitle = f"Patient: {patient_name} | Profile: {self.blood_group}, {self.profession}"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((img_width - subtitle_width) // 2, 50), subtitle, fill=self.COLORS['TEXT'], font=font_medium)

    def _calculate_annotation_positions(self, num_items: int, img_width: int, img_height: int) -> List[Tuple[int, int]]:
        positions = []
        margin_x, margin_y = 80, 100
        title_space, legend_space = 90, 140
        usable_width = img_width - 2 * margin_x
        usable_height = img_height - title_space - legend_space - margin_y
        
        if num_items <= 3: cols = num_items
        elif num_items <= 6: cols = 3
        elif num_items <= 12: cols = 4
        else: cols = 5
        
        rows = (num_items + cols - 1) // cols
        spacing_x = usable_width // cols if cols > 0 else usable_width
        spacing_y = usable_height // rows if rows > 0 else usable_height
        
        for i in range(num_items):
            row, col = i // cols, i % cols
            x = margin_x + col * spacing_x + spacing_x // 2
            y = title_space + margin_y // 2 + row * spacing_y + spacing_y // 2
            positions.append((x, y))
        return positions

    def _draw_food_annotation(self, draw: ImageDraw, x: int, y: int, food_name: str, calories: int, risk_level: str, font_medium, font_small):
        if risk_level == 'SAFE': text_color = (46, 204, 113)
        elif risk_level == 'CAUTION': text_color = (241, 196, 15)
        else: text_color = (231, 76, 60)
        
        name_text = (food_name[:16] + "..") if len(food_name) > 18 else food_name
        calorie_text = f"{calories} kcal"
        
        name_bbox = draw.textbbox((0, 0), name_text, font=font_medium)
        name_w, name_h = name_bbox[2]-name_bbox[0], name_bbox[3]-name_bbox[1]
        
        text_x, text_y = x + 60 - name_w // 2, y
        padding = 4
        draw.rectangle([(text_x - padding, text_y - padding), (text_x + name_w + padding, text_y + name_h + padding)], fill=(0, 0, 0, 200))
        draw.text((text_x, text_y), name_text, fill=text_color, font=font_medium)
        
        cal_bbox = draw.textbbox((0, 0), calorie_text, font=font_small)
        cal_w, cal_h = cal_bbox[2]-cal_bbox[0], cal_bbox[3]-cal_bbox[1]
        cal_x, cal_y = text_x + (name_w - cal_w) // 2, text_y + name_h + padding + 3
        draw.rectangle([(cal_x-3, cal_y-3), (cal_x+cal_w+3, cal_y+cal_h+3)], fill=(0, 0, 0, 180))
        draw.text((cal_x, cal_y), calorie_text, fill=text_color, font=font_small)
        
        ax1, ay1 = text_x - padding, text_y + name_h // 2
        draw.line([(ax1, ay1), (x, y)], fill=text_color, width=3)
        
        # Arrowhead
        dx, dy = x - ax1, y - ay1
        angle = math.atan2(dy, dx)
        asize = 8
        tip = (x, y)
        p1 = (x - asize * math.cos(angle - math.pi/6), y - asize * math.sin(angle - math.pi/6))
        p2 = (x - asize * math.cos(angle + math.pi/6), y - asize * math.sin(angle + math.pi/6))
        draw.polygon([tip, p1, p2], fill=text_color)

    def _add_legend(self, draw: ImageDraw, img_width: int, img_height: int, font_medium, font_small):
        ly, lx = img_height - 120, 20
        draw.rectangle([(lx-10, ly-10), (lx+250, ly+90)], fill=(0,0,0,180))
        draw.text((lx, ly), "Safety Legend:", fill=(255,255,255), font=font_medium)
        items = [('SAFE', 'Safe to eat', (46, 204, 113)), ('CAUTION', 'Eat with caution', (241, 196, 15)), ('UNSAFE', 'Avoid completely', (231, 76, 60))]
        for i, (lvl, desc, clr) in enumerate(items):
            yo = ly + 25 + i * 20
            draw.ellipse([(lx, yo), (lx+15, yo+15)], fill=clr, outline=(255,255,255), width=2)
            draw.text((lx+25, yo), desc, fill=(255,255,255), font=font_small)

    def _add_summary_panel(self, draw: ImageDraw, img_width: int, img_height: int, font_medium, font_small):
        px, py = img_width - 280, img_height - 150
        s, c, u = 0, 0, 0
        for item in self.risk_analysis:
            lvl = item.get('risk_level')
            if lvl == 'SAFE': s += 1
            elif lvl == 'CAUTION': c += 1
            elif lvl == 'UNSAFE': u += 1
        
        draw.rectangle([(px-10, py-10), (img_width-10, py+120)], fill=(0,0,0,180))
        draw.text((px, py), "Summary:", fill=(255,255,255), font=font_medium)
        stats = [f"Total Items: {len(self.food_items)}", f"S: {s} | C: {c} | U: {u}", f"Date: {datetime.now().strftime('%Y-%m-%d')}"]
        for i, txt in enumerate(stats):
            draw.text((px, py + 25 + i * 20), txt, fill=(255,255,255), font=font_small)


class NumberedCanvas(canvas.Canvas):
    """Custom canvas with watermark and page numbers (same as original)"""
    
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
                x, y = (letter[0] - logo_size) / 2, (letter[1] - logo_size) / 2
                self.drawImage(self.logo_path, x, y, width=logo_size, height=logo_size, 
                             mask='auto', preserveAspectRatio=True)
                self.restoreState()
            except: pass
        
        # Header
        if page_num > 1:
            self.saveState()
            self.setFont('Helvetica-Bold', 10)
            self.setFillColor(COLORS['primary'])
            self.drawString(0.75 * inch, letter[1] - 0.5 * inch, "AGENIX AI TEAM")
            self.setStrokeColor(COLORS['border'])
            self.setLineWidth(0.5)
            self.line(0.75 * inch, letter[1] - 0.6 * inch, letter[0] - 0.75 * inch, letter[1] - 0.6 * inch)
            self.restoreState()
        
        # Footer
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColor(COLORS['text'])
        self.drawCentredString(letter[0] / 2, 0.5 * inch, f"Page {page_num} of {page_count}")
        self.setStrokeColor(COLORS['border'])
        self.setLineWidth(0.5)
        self.line(0.75 * inch, 0.7 * inch, letter[0] - 0.75 * inch, 0.7 * inch)
        self.restoreState()


def get_styles():
    """Get custom paragraph styles (same as original)"""
    styles = getSampleStyleSheet()
    
    # Only add custom styles if they don't already exist
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
            textColor=COLORS['text'], spaceAfter=8, fontName='Helvetica'
        ))
    
    # Add table-specific styles
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


def create_cover_page(patient_info, meal_info, risk_summary, logo_path):
    """Page 1: Cover Page - Compact Design (SAME AS ORIGINAL)"""
    story, styles = [], getSampleStyleSheet()
    
    # Logo - smaller size
    if Path(logo_path).exists():
        try:
            logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
            logo.hAlign = 'CENTER'
            story.extend([logo, Spacer(1, 0.15*inch)])
        except: pass
    
    # Title - more compact
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24,
                                textColor=COLORS['primary'], spaceAfter=12,
                                alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    story.append(Paragraph("AGENIX AI TEAM", title_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Report title - smaller
    report_title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'], fontSize=18,
                                       textColor=COLORS['primary'], spaceAfter=15,
                                       alignment=TA_CENTER, fontName='Helvetica-Bold')
    story.append(Paragraph("FOOD SAFETY & RISK ASSESSMENT REPORT", report_title_style))
    story.append(Spacer(1, 0.25*inch))
    
    # Patient table - more compact
    patient_data = [
        ['Patient:', patient_info.get('name', 'Unknown')],
        ['Age/BMI:', f"{patient_info.get('age', 'N/A')} yrs | BMI: {patient_info.get('bmi', 'N/A')}"],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['ID:', f"FSAR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLORS['light_gray']),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Meal info - compact single line
    meal_style = ParagraphStyle('MealInfo', parent=styles['Normal'], fontSize=11,
                                textColor=COLORS['text'], spaceAfter=8,
                                alignment=TA_CENTER, fontName='Helvetica')
    
    meal_text = f"<b>Meal:</b> {meal_info.get('meal_type', 'Unknown')} | <b>Cuisine:</b> {meal_info.get('cuisine_type', 'Unknown')}"
    story.append(Paragraph(meal_text, meal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Risk assessment box - more compact
    risk_level = risk_summary.get('risk_level', 'UNKNOWN')
    risk_score = risk_summary.get('risk_score', 0)
    confidence = risk_summary.get('confidence_score', 0)
    
    risk_color = COLORS['safe'] if risk_level == 'SAFE' else COLORS['caution'] if risk_level == 'CAUTION' else COLORS['unsafe']
    risk_emoji = '✅' if risk_level == 'SAFE' else '⚠️' if risk_level == 'CAUTION' else '🚨'
    
    # Compact risk box
    risk_box_style = ParagraphStyle('RiskBox', parent=styles['Normal'], fontSize=14,
                                   textColor=COLORS['text'], spaceAfter=6,
                                   alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    risk_data = [
        [Paragraph('<b>OVERALL RISK ASSESSMENT</b>', risk_box_style)],
        [Paragraph(f'<font color="{risk_color.hexval()}" size="20"><b>{risk_emoji} {risk_level}</b></font>', risk_box_style)],
        [Paragraph(f'Risk Score: {risk_score}/100 | Confidence: {confidence:.0%}', meal_style)],
    ]
    
    risk_table = Table(risk_data, colWidths=[5*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['light_gray']),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 2, risk_color),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(risk_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer - compact
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9,
                                 textColor=COLORS['text'], alignment=TA_CENTER,
                                 fontName='Helvetica-Oblique')
    story.append(Paragraph("Generated by FIP AI Health Analysis System v1.0", footer_style))
    
    return story



def create_annotated_image_page(state):
    """Page 3: Full-page annotated food image with color-coded safety indicators"""
    story, styles = [], get_styles()
    
    # Title
    story.append(Paragraph("ANNOTATED FOOD IMAGE ANALYSIS", styles['SectionTitle']))
    story.append(Spacer(1, 0.2*inch))
    
    # Get annotated image path from state
    annotated_img_path = state.get('annotated_image_path')
    
    # DEBUG: Log what we're getting
    logger.info(f"🔍 DEBUG: annotated_image_path from state: {annotated_img_path}")
    logger.info(f"🔍 DEBUG: Type: {type(annotated_img_path)}")
    
    if annotated_img_path:
        img_path_obj = Path(annotated_img_path)
        logger.info(f"🔍 DEBUG: Path exists: {img_path_obj.exists()}")
        logger.info(f"🔍 DEBUG: Absolute path: {img_path_obj.resolve()}")
    
    if annotated_img_path and Path(annotated_img_path).exists():
        # Add description
        desc_style = ParagraphStyle(
            'ImageDesc',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLORS['text'],
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        story.append(Paragraph(
            "Food items are color-coded by safety level for easy identification",
            desc_style
        ))
        story.append(Spacer(1, 0.1*inch))
        
        # Add full-page annotated image - reduced size slightly to prevent blank pages
        try:
            # Scaled to fit comfortably on 8.5x11 page with margins
            img_width, img_height = 6.5*inch, 7.5*inch
            img = Image(annotated_img_path, width=img_width, height=img_height)
            img.hAlign = 'CENTER'
            story.append(img)
            
            # Add legend caption
            caption_style = ParagraphStyle(
                'Caption',
                parent=styles['Normal'],
                fontSize=9,
                textColor=COLORS['text'],
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            )
            
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(
                '<font color="#E74C3C"><b>RED</b></font> = Unsafe | '
                '<font color="#F1C40F"><b>YELLOW</b></font> = Caution | '
                '<font color="#2ECC71"><b>GREEN</b></font> = Safe',
                caption_style
            ))
            
            logger.info("✅ Added annotated image to PDF")
            
        except Exception as e:
            logger.warning(f"Could not add annotated image: {e}")
            import traceback
            traceback.print_exc()
            story.append(Paragraph(
                f"Annotated image could not be loaded: {e}",
                styles['Normal']
            ))
    else:
        # No annotated image available
        error_msg = "Annotated food image not available"
        if annotated_img_path:
            error_msg += f" (Path provided but file not found: {annotated_img_path})"
        else:
            error_msg += " (No path provided in state)"
        
        story.append(Paragraph(error_msg, styles['Normal']))
        logger.warning(f"⚠️  {error_msg}")
    
    return story

def create_fsar_table_page(state):
    """Page 2: FSAR Table - Food Safety Assessment Table (NEW)"""
    story, styles = [], get_styles()
    
    story.append(Paragraph("FOOD SAFETY ASSESSMENT TABLE", styles['SectionTitle']))
    story.append(Spacer(1, 0.15*inch))
    
    # Get food items and organize by risk level
    risk_items = state.get('food_item_risk_analysis', [])
    identified_items = state.get('identified_food_items', [])  # For calories lookup
    
    safe_items = [item for item in risk_items if item.get('risk_level') == 'SAFE']
    caution_items = [item for item in risk_items if item.get('risk_level') == 'CAUTION']
    unsafe_items = [item for item in risk_items if item.get('risk_level') == 'UNSAFE']
    
    # Summary statistics box
    summary_style = ParagraphStyle('Summary', parent=styles['Normal'], fontSize=10,
                                  textColor=COLORS['text'], alignment=TA_CENTER,
                                  fontName='Helvetica-Bold')
    
    summary_data = [
        [Paragraph(f'<b>Total Items: {len(risk_items)}</b>', summary_style),
         Paragraph(f'<font color="{COLORS["safe"].hexval()}">✅ Safe: {len(safe_items)}</font>', summary_style),
         Paragraph(f'<font color="{COLORS["caution"].hexval()}">⚠️ Caution: {len(caution_items)}</font>', summary_style),
         Paragraph(f'<font color="{COLORS["unsafe"].hexval()}">🚨 Critical: {len(unsafe_items)}</font>', summary_style)]
    ]
    
    summary_table = Table(summary_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['light_gray']),
        ('GRID', (0, 0), (-1, -1), 1, COLORS['border']),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Table header
    table_data = [
        [
            Paragraph('<b>Food Item</b>', styles['TableHeader']),
            Paragraph('<b>Calories</b>', styles['TableHeader']),
            Paragraph('<b>Risk Level</b>', styles['TableHeader']),
            Paragraph('<b>Confidence</b>', styles['TableHeader']),
            Paragraph('<b>Risk Factor</b>', styles['TableHeader']),
            Paragraph('<b>Severity/Effect</b>', styles['TableHeader']),
            Paragraph('<b>Alternative</b>', styles['TableHeader']),
        ]
    ]
    
    # Add safe items first
    if safe_items:
        for item in safe_items:
            table_data.append(create_table_row(item, styles, 'SAFE', identified_items))
    
    # Add caution items
    if caution_items:
        for item in caution_items:
            table_data.append(create_table_row(item, styles, 'CAUTION', identified_items))
    
    # Add unsafe/critical items
    if unsafe_items:
        for item in unsafe_items:
            table_data.append(create_table_row(item, styles, 'UNSAFE', identified_items))
    
    # Create table with optimized column widths
    col_widths = [3*cm, 1.3*cm, 1.8*cm, 1.5*cm, 3.2*cm, 2.2*cm, 3*cm]
    
    food_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Apply table styling
    table_style = [
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('PADDING', (0, 0), (-1, -1), 3),
        
        # Body styling
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Calories center
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Risk level center
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Confidence center
    ]
    
    # Color code rows by risk level
    row_num = 1
    for item in safe_items:
        table_style.append(('BACKGROUND', (0, row_num), (-1, row_num), HexColor('#E8F5E9')))
        row_num += 1
    
    for item in caution_items:
        table_style.append(('BACKGROUND', (0, row_num), (-1, row_num), HexColor('#FFF9C4')))
        row_num += 1
    
    for item in unsafe_items:
        table_style.append(('BACKGROUND', (0, row_num), (-1, row_num), HexColor('#FFEBEE')))
        row_num += 1
    
    food_table.setStyle(TableStyle(table_style))
    
    story.append(food_table)
    story.append(Spacer(1, 0.2*inch))
    
    # NOTE: Original food image removed from here
    # The annotated image with colored arrows will appear on Page 3
    
    return story


def create_table_row(item, styles, risk_level, identified_items):
    """Create a single table row for a food item"""
    name = item.get('name', 'Unknown')
    
    # Get calories by matching name from identified_food_items
    calories_text = "N/A"
    for identified_item in identified_items:
        if identified_item.get('name') == name:
            calories = identified_item.get('calories')
            if calories is not None and isinstance(calories, (int, float)):
                calories_text = f"{int(calories)}"
            break
    
    # Risk level with emoji
    risk_emoji = '✅' if risk_level == 'SAFE' else '⚠️' if risk_level == 'CAUTION' else '🚨'
    risk_text = f"{risk_emoji} {risk_level}"
    
    # Confidence
    confidence = item.get('confidence_level', 0)
    confidence_text = f"{confidence:.0%}" if isinstance(confidence, (int, float)) else str(confidence)
    
    # Risk factors
    risk_factors = item.get('risk_factors', [])
    if risk_factors and len(risk_factors) > 0:
        primary_risk = risk_factors[0].get('factor', 'None')[:40]  # Truncate if too long
        severity = risk_factors[0].get('severity', 'N/A')
    else:
        primary_risk = 'None identified'
        severity = 'N/A'
    
    # Alternatives
    alternatives = item.get('alternatives', [])
    if alternatives and len(alternatives) > 0:
        alt_text = ', '.join(alternatives[:2])[:35]  # Show first 2, truncate
    else:
        alt_text = 'N/A'
    
    # Create row with wrapped text
    return [
        Paragraph(f'<b>{name}</b>', styles['TableCell']),
        Paragraph(calories_text, styles['TableCell']),
        Paragraph(risk_text, styles['TableCell']),
        Paragraph(confidence_text, styles['TableCell']),
        Paragraph(primary_risk, styles['TableCell']),
        Paragraph(severity, styles['TableCell']),
        Paragraph(alt_text, styles['TableCell']),
    ]



# ----------------------------------------------------------------------------
# COMPONENT: COMPLETE REPORT GENERATION FUNCTIONS (Consolidated)
# ----------------------------------------------------------------------------



def create_food_item_analysis(state):
    """Pages 3-4: Detailed Food Item Analysis"""
    story, styles = [], get_styles()
    
    story.append(Paragraph("DETAILED FOOD ITEM ANALYSIS", styles['SectionTitle']))
    story.append(Spacer(1, 0.2*inch))
    
    risk_items = state.get('food_item_risk_analysis', [])
    
    # Group by risk level
    unsafe_items = [item for item in risk_items if item.get('risk_level') == 'UNSAFE']
    caution_items = [item for item in risk_items if item.get('risk_level') == 'CAUTION']
    safe_items = [item for item in risk_items if item.get('risk_level') == 'SAFE']
    
    # Unsafe items
    if unsafe_items:
        story.append(Paragraph(f"🚨 UNSAFE ITEMS ({len(unsafe_items)} items) - AVOID OR MODIFY", styles['SubSection']))
        story.append(Spacer(1, 0.1*inch))
        
        for item in unsafe_items[:5]:  # Show first 5
            story.extend(create_food_item_box(item, styles))
    
    if len(story) > 10:  # Add page break if needed
        story.append(PageBreak())
    
    # Caution items
    if caution_items:
        story.append(Paragraph(f"⚠️ CAUTION ITEMS ({len(caution_items)} items) - EAT WITH MODIFICATIONS", styles['SubSection']))
        story.append(Spacer(1, 0.1*inch))
        
        for item in caution_items[:5]:
            story.extend(create_food_item_box(item, styles))
    
    # Safe items (brief list)
    if safe_items:
        story.append(Paragraph(f"✅ SAFE ITEMS ({len(safe_items)} items) - ENJOY IN MODERATION", styles['SubSection']))
        story.append(Spacer(1, 0.1*inch))
        
        for item in safe_items[:10]:
            name = item.get('name', 'Unknown')
            risk_score = item.get('risk_score', 0)
            story.append(Paragraph(f"• {name} (Risk: {risk_score}/100)", styles['BodyText']))
    
    return story


def create_food_item_box(item, styles):
    """Create detailed box for a single food item"""
    elements = []
    
    name = item.get('name', 'Unknown')
    risk_level = item.get('risk_level', 'UNKNOWN')
    risk_score = item.get('risk_score', 0)
    confidence = item.get('confidence_level', 0)
    
    # Determine color
    risk_color = COLORS['safe'] if risk_level == 'SAFE' else COLORS['caution'] if risk_level == 'CAUTION' else COLORS['unsafe']
    risk_emoji = '✅' if risk_level == 'SAFE' else '⚠️' if risk_level == 'CAUTION' else '🚨'
    
    # Item header
    header_text = f"<b>{risk_emoji} {name}</b>"
    elements.append(Paragraph(header_text, styles['SubSection']))
    
    # Risk info
    risk_text = f"""
    <b>Risk Level:</b> <font color="{risk_color.hexval()}">{risk_level}</font><br/>
    <b>Risk Score:</b> {risk_score}/100 | <b>Confidence:</b> {confidence:.0%}
    """
    elements.append(Paragraph(risk_text, styles['BodyText']))
    
    # Risk factors
    risk_factors = item.get('risk_factors', [])[:3]
    if risk_factors:
        elements.append(Paragraph("<b>⚠️ Risk Factors:</b>", styles['BodyText']))
        for factor in risk_factors:
            factor_text = f"• <b>{factor.get('severity', 'UNKNOWN')}:</b> {factor.get('factor', 'Unknown')}"
            if factor.get('medical_basis'):
                factor_text += f"<br/>  <i>Medical Basis: {factor.get('medical_basis')}</i>"
            elements.append(Paragraph(factor_text, styles['BodyText']))
    
    # Recommendation
    recommendation = item.get('recommendation', '')
    if recommendation:
        elements.append(Paragraph(f"<b>✅ Recommendation:</b> {recommendation}", styles['BodyText']))
    
    # Alternatives
    alternatives = item.get('alternatives', [])
    if alternatives:
        alt_text = f"<b>💡 Alternatives:</b> {', '.join(alternatives[:3])}"
        elements.append(Paragraph(alt_text, styles['BodyText']))
    
    elements.append(Spacer(1, 0.15*inch))
    
    return elements


def create_nutritional_compliance(state):
    """Page 5: Nutritional Compliance"""
    story, styles = [], get_styles()
    
    story.append(Paragraph("NUTRITIONAL COMPLIANCE ANALYSIS", styles['SectionTitle']))
    story.append(Spacer(1, 0.2*inch))
    
    health_metrics = state.get('health_metrics', {})
    
    # Create compliance tables for each nutrient
    nutrients = [
        ('Calories', 'calorie_compliance'),
        ('Sodium', 'sodium_compliance'),
        ('Sugar', 'sugar_compliance'),
        ('Saturated Fat', 'fat_compliance'),
    ]
    
    for nutrient_name, key in nutrients:
        compliance = health_metrics.get(key, {})
        if compliance:
            story.extend(create_nutrient_bar(nutrient_name, compliance, styles))
    
    return story


def create_nutrient_bar(nutrient_name, compliance, styles):
    """Create visual nutrient compliance bar"""
    elements = []
    
    consumed = compliance.get('consumed', 0)
    limit = compliance.get('recommended') or compliance.get('limit', 0)
    percentage = compliance.get('percentage', 0)
    status = compliance.get('status', 'UNKNOWN')
    
    # Determine color
    if status == 'WITHIN_LIMIT':
        color = COLORS['safe']
        emoji = '✅'
    elif status == 'OVER_LIMIT':
        color = COLORS['unsafe']
        emoji = '🚨'
    else:
        color = COLORS['caution']
        emoji = '⚠️'
    
    # Create table
    data = [
        [Paragraph(f"<b>{nutrient_name}</b>", styles['SubSection'])],
        [Paragraph(f"Consumed: {consumed} | Limit: {limit}", styles['BodyText'])],
        [Paragraph(f"<font color='{color.hexval()}'><b>{emoji} {status} ({percentage:.1f}%)</b></font>", styles['BodyText'])],
    ]
    
    table = Table(data, colWidths=[6*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['light_gray']),
        ('BOX', (0, 0), (-1, -1), 1, color),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.15*inch))
    
    return elements


def create_medical_interactions(state):
    """Page 6: Medical Interactions & Warnings"""
    story, styles = [], get_styles()
    
    story.append(Paragraph("MEDICAL INTERACTIONS & WARNINGS", styles['SectionTitle']))
    story.append(Spacer(1, 0.2*inch))
    
    warnings = state.get('warnings', [])
    
    # Critical warnings
    critical_warnings = [w for w in warnings if w.get('severity') == 'CRITICAL']
    if critical_warnings:
        story.append(Paragraph("🚨 CRITICAL WARNINGS", styles['SubSection']))
        
        for warning in critical_warnings:
            warning_text = f"""
            <b>{warning.get('type', 'UNKNOWN')}:</b> {warning.get('message', 'No details')}<br/>
            <b>Affected Items:</b> {', '.join(warning.get('affected_items', [])[:5])}<br/>
            <b>Action Required:</b> {warning.get('action_required', 'Consult healthcare provider')}
            """
            story.append(Paragraph(warning_text, styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
    
    # Drug-food interactions
    interactions = state.get('drug_food_interactions', [])
    if interactions:
        story.append(Paragraph("💊 MEDICATION INTERACTIONS", styles['SubSection']))
        
        for interaction in interactions[:5]:
            int_text = f"""
            <b>Medication:</b> {interaction.get('medication', 'Unknown')}<br/>
            <b>Food Item:</b> {interaction.get('food_item', 'Unknown')}<br/>
            <b>Interaction:</b> {interaction.get('interaction_type', 'Unknown')}<br/>
            <b>Recommendation:</b> {interaction.get('recommendation', 'Consult doctor')}
            """
            story.append(Paragraph(int_text, styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
    
    return story


def create_recommendations(state):
    """Page 7: Personalized Recommendations"""
    story, styles = [], get_styles()
    
    story.append(Paragraph("PERSONALIZED RECOMMENDATIONS", styles['SectionTitle']))
    story.append(Spacer(1, 0.2*inch))
    
    recommendations = state.get('personalized_recommendations', {})
    
    # Meal modifications
    modifications = recommendations.get('meal_modifications', [])
    if modifications:
        story.append(Paragraph("💡 MEAL MODIFICATIONS", styles['SubSection']))
        for idx, mod in enumerate(modifications[:10], 1):
            story.append(Paragraph(f"{idx}. {mod}", styles['BodyText']))
        story.append(Spacer(1, 0.15*inch))
    
    # Avoid completely
    avoid = recommendations.get('avoid_completely', [])
    if avoid:
        story.append(Paragraph("🚫 AVOID COMPLETELY", styles['SubSection']))
        for item in avoid[:5]:
            avoid_text = f"""
            <b>Item:</b> {item.get('item', 'Unknown')}<br/>
            <b>Reason:</b> {item.get('reason', 'No details')}<br/>
            <b>Alternative:</b> {item.get('alternative', 'Consult nutritionist')}
            """
            story.append(Paragraph(avoid_text, styles['BodyText']))
            story.append(Spacer(1, 0.1*inch))
    
    # Timing recommendations
    timing = recommendations.get('timing_recommendations', [])
    if timing:
        story.append(Paragraph("⏰ TIMING RECOMMENDATIONS", styles['SubSection']))
        for rec in timing[:5]:
            story.append(Paragraph(f"• {rec}", styles['BodyText']))
    
    return story


def create_medical_insights(state):
    """Page 8: Medical Purpose Insights"""
    story, styles = [], get_styles()
    
    story.append(Paragraph("MEDICAL PURPOSE INSIGHTS", styles['SectionTitle']))
    story.append(Spacer(1, 0.2*inch))
    
    insights = state.get('medical_purpose_insights', {})
    
    # Handle case where insights might be empty or not a dict
    if not insights or not isinstance(insights, dict):
        story.append(Paragraph("No medical insights available.", styles['BodyText']))
        return story
    
    # Chronic disease impact
    disease_impact = insights.get('chronic_disease_impact', {})
    if disease_impact:
        story.append(Paragraph("🏥 CHRONIC DISEASE IMPACT", styles['SubSection']))
        
        # Handle both dict and string types
        if isinstance(disease_impact, dict):
            for disease, impact in disease_impact.items():
                story.append(Paragraph(f"<b>{disease}:</b> {impact}", styles['BodyText']))
        elif isinstance(disease_impact, str):
            story.append(Paragraph(disease_impact, styles['BodyText']))
        
        story.append(Spacer(1, 0.15*inch))
    
    # Monitoring parameters
    monitoring = insights.get('monitoring_parameters', [])
    if monitoring:
        story.append(Paragraph("📊 MONITORING PARAMETERS", styles['SubSection']))
        
        # Handle both list and string types
        if isinstance(monitoring, list):
            for param in monitoring[:5]:
                story.append(Paragraph(f"• {param}", styles['BodyText']))
        elif isinstance(monitoring, str):
            story.append(Paragraph(monitoring, styles['BodyText']))
        
        story.append(Spacer(1, 0.15*inch))
    
    # Exercise recommendations
    exercise = insights.get('exercise_recommendations', '')
    if exercise:
        story.append(Paragraph("🏃 EXERCISE RECOMMENDATIONS", styles['SubSection']))
        story.append(Paragraph(str(exercise), styles['BodyText']))
    
    # Long-term health impact
    long_term = insights.get('long_term_health_impact', '')
    if long_term:
        story.append(Paragraph("📅 LONG-TERM HEALTH IMPACT", styles['SubSection']))
        story.append(Paragraph(str(long_term), styles['BodyText']))
    
    # Hydration needs
    hydration = insights.get('hydration_needs', '')
    if hydration:
        story.append(Paragraph("💧 HYDRATION NEEDS", styles['SubSection']))
        story.append(Paragraph(str(hydration), styles['BodyText']))
    
    return story


def create_statistical_summary(state):
    """Page 9: Statistical Summary"""
    story, styles = [], get_styles()
    
    story.append(Paragraph("STATISTICAL SUMMARY", styles['SectionTitle']))
    story.append(Spacer(1, 0.2*inch))
    
    overall = state.get('overall_risk_assessment', {})
    validation = state.get('validation_summary', {})
    
    # Summary table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Items Analyzed', str(len(state.get('identified_food_items', [])))],
        ['Safe Items', f"{overall.get('safe_items_count', 0)} ({overall.get('safe_percentage', 0):.1f}%)"],
        ['Unsafe Items', f"{overall.get('unsafe_items_count', 0)} ({overall.get('unsafe_percentage', 0):.1f}%)"],
        ['Overall Risk Score', f"{overall.get('risk_score', 0)}/100"],
        ['Safety Score', f"{validation.get('overall_safety_score', 0)}/100"],
        ['Total Conflicts', str(validation.get('total_conflicts', 0))],
        ['Critical Issues', str(validation.get('critical_issues', 0))],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), COLORS['light_gray']),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(summary_table)
    
    return story


def create_appendix(state):
    """Page 10: Appendix & Disclaimers"""
    story, styles = [], get_styles()
    
    story.append(Paragraph("APPENDIX", styles['SectionTitle']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("📚 METHODOLOGY", styles['SubSection']))
    methodology_text = """
    This report was generated using the FIP (Food Image Processing) AI Health Analysis System, 
    which employs Computer Vision (Gemini AI) for food identification, Medical NLP (Groq LLM) 
    for report processing, Health Metrics Analysis for conflict detection, and Risk Assessment 
    with confidence scoring.
    """
    story.append(Paragraph(methodology_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("⚠️ DISCLAIMERS", styles['SubSection']))
    disclaimer_text = """
    1. This report is for informational purposes only and does not constitute medical advice.<br/>
    2. Consult your healthcare provider before making significant dietary changes.<br/>
    3. Food identification and nutritional estimates are based on AI analysis and may have variations.<br/>
    4. Individual responses to foods may vary based on metabolism, medications, and other factors.<br/>
    5. In case of emergency or severe symptoms, seek immediate medical attention.
    """
    story.append(Paragraph(disclaimer_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("📞 CONTACT INFORMATION", styles['SubSection']))
    contact_text = f"""
    <b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
    <b>Report ID:</b> {state.get('final_report', {}).get('report_id', 'N/A')}<br/>
    <b>Version:</b> 1.0<br/><br/>
    © 2025 FIP Health Analysis System by Agenix AI Team. All rights reserved.
    """
    story.append(Paragraph(contact_text, styles['BodyText']))
    
    return story


def FIP_report_generator_fsar(state: FIPState) -> FIPState:
    """
    Generate FSAR PDF report with table-based page 2
    
    Args:
        state: Complete FIP state with all analysis data
        
    Returns:
        Updated state with report paths and metadata
    """
    logger.info("📄 Generating FSAR PDF report with table-based layout")
    
    try:
        # Create output directory
        output_dir = Path("data/outputs/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_name = state.get('patient_info', {}).get('name', 'unknown').replace(' ', '_').lower()
        pdf_filename = f"fsar_report_{patient_name}_{timestamp}.pdf"
        pdf_path = output_dir / pdf_filename
        
        # CRITICAL DEBUG
        logger.info(f"DEBUG: [FSAR BUG HUNT] state keys: {list(state.keys())}")
        logger.info(f"DEBUG: [FSAR BUG HUNT] annotated_image_path: {state.get('annotated_image_path')}")
        
        # Logo path
        logo_path = "assets/agenix_logo.png"
        if not Path(logo_path).exists():
            logo_path = "e:/fip/assets/agenix_logo.png"

        # ====================================================================
        # NEW: INTERNAL ANNOTATED IMAGE GENERATION
        # ====================================================================
        logger.info("🎨 Internal Step: Checking for annotated food image...")
        annotated_path = state.get('annotated_image_path')
        
        if not annotated_path or not Path(annotated_path).exists():
            logger.info("🛠️  Generating annotated image internally...")
            try:
                generator = AnnotatedReportGenerator(state)
                annotated_path = generator.generate_annotated_image()
                state['annotated_image_path'] = annotated_path
                logger.info(f"✅ Internal annotation success: {annotated_path}")
            except Exception as e:
                logger.error(f"❌ Internal annotation failed: {e}")
                import traceback
                traceback.print_exc()

        # Build complete story
        doc = SimpleDocTemplate(
            str(pdf_path), pagesize=letter,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=1*inch, bottomMargin=1*inch
        )
        
        # Build complete story
        story = []
        
        # Page 1: Cover (SAME AS ORIGINAL)
        logger.info("Adding cover page...")
        story.extend(create_cover_page(
            state.get('patient_info', {}),
            {'meal_type': state.get('meal_type', 'Unknown'),
             'cuisine_type': state.get('cuisine_type', 'Unknown')},
            state.get('overall_risk_assessment', {}),
            logo_path
        ))
        story.append(PageBreak())
        
        # Page 2: FSAR Table
        logger.info("Adding FSAR table page...")
        story.extend(create_fsar_table_page(state))
        story.append(PageBreak())
        
        # Page 3: ANNOTATED IMAGE (NEW!)
        logger.info("Adding annotated food image page...")
        story.extend(create_annotated_image_page(state))
        story.append(PageBreak())
        
        # Pages 3-4: Food Item Analysis (SAME AS ORIGINAL)
        logger.info("Adding food item analysis...")
        story.extend(create_food_item_analysis(state))
        story.append(PageBreak())
        
        # Page 5: Nutritional Compliance (SAME AS ORIGINAL)
        logger.info("Adding nutritional compliance...")
        story.extend(create_nutritional_compliance(state))
        story.append(PageBreak())
        
        # Page 6: Medical Interactions (SAME AS ORIGINAL)
        logger.info("Adding medical interactions...")
        story.extend(create_medical_interactions(state))
        story.append(PageBreak())
        
        # Page 7: Recommendations (SAME AS ORIGINAL)
        logger.info("Adding recommendations...")
        story.extend(create_recommendations(state))
        story.append(PageBreak())
        
        # Page 8: Medical Insights (SAME AS ORIGINAL)
        logger.info("Adding medical insights...")
        story.extend(create_medical_insights(state))
        story.append(PageBreak())
        
        # Page 9: Statistical Summary (SAME AS ORIGINAL)
        logger.info("Adding statistical summary...")
        story.extend(create_statistical_summary(state))
        story.append(PageBreak())
        
        # Page 10: Appendix (SAME AS ORIGINAL)
        logger.info("Adding appendix...")
        story.extend(create_appendix(state))
        
        # Build PDF
        logger.info("Building FSAR PDF with custom canvas...")
        doc.build(story, canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, logo_path=logo_path, **kwargs))
        
        logger.info(f"✅ FSAR PDF report generated: {pdf_path}")
        
        # Update state
        state["final_report"] = {
            "pdf_path": str(pdf_path),
            "generated_at": datetime.now().isoformat(),
            "report_id": f"FSAR-{timestamp}",
            "total_pages": 10,
            "report_type": "FSAR"
        }
        
        state["export_formats"] = {"pdf": str(pdf_path)}
        
        state["statistical_summary"] = {
            "total_items_analyzed": len(state.get('identified_food_items', [])),
            "safe_items_count": state.get('overall_risk_assessment', {}).get('safe_items_count', 0),
            "unsafe_items_count": state.get('overall_risk_assessment', {}).get('unsafe_items_count', 0)
        }
        
        state["quality_assurance"] = {
            "report_generated": True,
            "format": "PDF",
            "validation_passed": True
        }
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Error generating FSAR report: {str(e)}")
        raise LLMException(f"FSAR report generation failed: {str(e)}", sys)


if __name__ == "__main__":
    print("=" * 70)
    print("📄 FIP - FSAR Report Generator (Table-Based Page 2)")
    print("=" * 70)
    print("\nThis node requires output from previous nodes.")
    print("Please run the complete FSAR workflow to test this node.")
